# instantiate
# ===========
# A simple script for instantiating projects from a template.

from collections import deque
import argparse
import fnmatch
import os
import pathlib
import shutil
import typing

import jinja2
import yaml


def _starts_with_k_digits(s, k):
    """Returns True iff s starts with k numbers."""
    if len(s) < k:
        return False
    return all(s[i].isdigit() for i in range(k))


def infer_next_project_number(path, k=2):
    """Looks through numbered folders in path and returns next number as a string.

    Directory names must start with a zero-padded, k-digit number. For 
    example, 02-homework, 03-homework, etc.

    Arguments
    ---------
    path
        The path to the directory to examine.
    k : int
        The number of digits in an assignment number. If None, then None is returned.

    Returns
    -------
    str
        The project number with k digits.
    
    """
    if k is None:
        return None

    path = pathlib.Path(path)
    directories = (x for x in path.iterdir() if x.is_dir())
    numbered_directories = (d for d in directories if _starts_with_k_digits(d.name, k))
    numbers = [int(d.name[:k]) for d in numbered_directories]

    if not numbers:
        number = 1
    else:
        number = max(numbers) + 1

    return format(number, "0" + str(k))


def render(src, dst, variables):
    """Renders the template at src, writes result to dst."""
    with src.open("r") as fileobj:
        # raise on undefined variables
        template = jinja2.Template(fileobj.read(), undefined=jinja2.StrictUndefined)
    with dst.open("w") as fileobj:
        try:
            fileobj.write(template.render(**variables))
        except jinja2.exceptions.UndefinedError as exc:
            raise RuntimeError(f"Problem replacing in {src}: {exc}")


def replace(directory, variables, no_replace=None, render=render):
    """Make Jinja2 substitutions in-place in all files under a directory.

    Parameters
    ----------
    directory : pathlib.Path
        The directory whose files will be rendered.
    variables : dictionary of dictionaries
        A dict of dicts containing the values available in substitutions. The
        outer dictionary keys are the outer context, and their inner keys
        are the names of the values.
    no_replace : Collection[str]
        A collection of fnmatch-style patterns of filenames on which
        replacement should not be performed. If None, replacement will be 
        performed on all files.

    """
    if no_replace is None:
        no_replace = []

    def _should_be_skipped(path):
        return any(fnmatch.fnmatch(path.name, pattern) for pattern in no_replace)

    # we'll do a BFS to find files and explore only directories that should
    # be explored; we could use os.walk, but this is slightly easier
    queue = deque([directory])
    while queue:
        current_directory = queue.popleft()

        for subpath in current_directory.iterdir():
            if _should_be_skipped(subpath):
                continue
            if subpath.is_file():
                render(src=subpath, dst=subpath, variables=variables)
            elif subpath.is_dir():
                queue.append(subpath)


def make_project(
    cwd,
    template_dir,
    project_name,
    *,
    context=None,
    numbering=None,
    no_replace=None,
    render=render,
):
    """Create a project from the given template.

    Parameters
    ----------
    cwd : pathlib.Path
        The current working directory, where the project will be created.
    template_dir : pathlib.Path
        Path to the template directory. Must obey the structure described below.
    project_name : str
        The name of the new project.
    context : dict
        A dictionary whose values will be variables to the templates.
    numbering : int
        Whether the project should be numbered and with how many digits.
        If None, no numbering is performed. Otherwise, this will be the number
        of digits in the project number.
    no_replace : Collection[str]
        A collection of fnmatch-style patterns of filenames on which
        replacement should not be performed. If None, replacement will be 
        performed on all files.

    Raises
    ------
    ValueError
        If the template does not exist.

    Notes
    -----
    The template is passed a dictionary of variables that can be used during
    rendering. The ``context`` dictionary provided to this function is
    available under the ``context`` key. In addition, the ``project`` key
    points to a dictionary containing ``number`` and ``name``, which hold the
    project's number and name respectively.

    """
    if not template_dir.exists():
        raise ValueError(f'Template "{template_dir}" does not exist.')

    if context is None:
        context = {}

    project_number = infer_next_project_number(cwd, numbering)

    # form the path to the new project directory
    if project_number is not None:
        dst_dir = cwd / (project_number + "-" + project_name)
    else:
        dst_dir = cwd / project_name

    shutil.copytree(template_dir, dst_dir)

    # replace
    variables = {
        "context": context,
        "project": {"number": project_number, "name": project_name},
    }
    replace(dst_dir, variables, no_replace=no_replace, render=render)


def cli(argv=None, cwd=None):
    """Command line interface.

    Parameters
    ----------
    argv : Sequence[str]
        A sequence of strings to use as arguments. If None, the arguments will
        be read from the command line using sys.argv.
    cwd : str
        The current working directory. If None, the process's cwd will be used.

    """
    if cwd is None:
        cwd = pathlib.Path.cwd()
    else:
        os.chdir(cwd)

    parser = argparse.ArgumentParser()
    parser.add_argument("template_dir", type=pathlib.Path)
    parser.add_argument("project_name")
    parser.add_argument("--numbering", type=int)
    parser.add_argument("--context", type=pathlib.Path)
    parser.add_argument("--no-replace", nargs="+")
    args = parser.parse_args(argv)

    context = {}
    if args.context is not None:
        with args.context.open() as fileobj:
            context[args.context.stem] = yaml.load(fileobj, Loader=yaml.Loader)

    try:
        make_project(
            cwd,
            args.template_dir,
            args.project_name,
            numbering=args.numbering,
            context=context,
            no_replace=args.no_replace,
        )
    except FileExistsError:
        print("Destination already exists. Not overwriting!")
    except Exception:
        if (cwd / args.project_name).exists():
            shutil.rmtree(cwd / args.project_name)
        raise


if __name__ == "__main__":
    cli()
