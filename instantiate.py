# instantiate
# ===========
# A simple script for instantiating projects from a template.

import argparse
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


def render(src, dst, contexts):
    """Renders the template at src, writes result to dst."""
    with src.open("r") as fileobj:
        template = jinja2.Template(fileobj.read())
    with dst.open("w") as fileobj:
        fileobj.write(template.render(**contexts))


def replace(directory, contexts):
    for path in directory.glob("**/*"):
        if path.is_file():
            render(path, path, contexts)


def make_project(cwd, template_dir, project_name, *, contexts=None, numbering=None):
    """Create a project from the given template.

    Parameters
    ----------
    cwd : pathlib.Path
        The current working directory, where the project will be created.
    template_dir : pathlib.Path
        Path to the template directory. Must obey the structure described below.
    project_name : str
        The name of the new project.
    contexts : dict
        A dictionary of dictionaries whose values will be available to the
        templates.
    numbering : int
        Whether the project should be numbered and with how many digits.
        If None, no numbering is performed. Otherwise, this will be the number
        of digits in the project number.

    Raises
    ------
    ValueError
        If the template does not exist.

    """
    if not template_dir.exists():
        raise ValueError(f'Template "{template_dir}" does not exist.')

    if contexts is None:
        contexts = {}

    project_number = infer_next_project_number(cwd, numbering)

    # form the path to the new project directory
    if project_number is not None:
        dst_dir = cwd / (project_number + "-" + project_name)
    else:
        dst_dir = cwd / project_name

    shutil.copytree(template_dir, dst_dir)

    # replace
    contexts["project"] = {"number": project_number, "name": project_name}
    replace(dst_dir, contexts)


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

    parser = argparse.ArgumentParser()
    parser.add_argument("template_dir", type=pathlib.Path)
    parser.add_argument("project_name")
    parser.add_argument("--numbering", type=int)
    parser.add_argument("--context", type=pathlib.Path)
    args = parser.parse_args(argv)

    contexts = {}
    if args.context is not None:
        with (cwd / args.context).open() as fileobj:
            contexts[args.context.stem] = yaml.load(fileobj, Loader=yaml.Loader)

    make_project(
        cwd,
        args.template_dir,
        args.project_name,
        numbering=args.numbering,
        contexts=contexts,
    )


if __name__ == "__main__":
    cli()