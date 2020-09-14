import pathlib
import os
import yaml

from pytest import fixture, raises

import instantiate


TEMPLATE_1_PATH = pathlib.Path(__file__).parent / "example_template_1"
TEMPLATE_2_PATH = pathlib.Path(__file__).parent / "example_template_2"


@fixture
def tempdir(tmpdir):
    return pathlib.Path(tmpdir)


def test_copy(tempdir):
    # when
    instantiate.cli([str(TEMPLATE_1_PATH), "foo"], cwd=tempdir)

    # then
    assert (tempdir / "foo" / "one").exists()
    assert (tempdir / "foo" / "two").exists()
    assert (tempdir / "foo" / "subdir").is_dir()
    assert (tempdir / "foo" / "subdir" / "a").exists()


def test_replacements(tempdir):
    # when
    instantiate.cli([str(TEMPLATE_1_PATH), "foo"], cwd=tempdir)

    with (tempdir / "foo" / "one").open() as fileobj:
        contents = fileobj.read()

    # then
    assert contents.strip() == "foo and None"


def test_additional_context(tempdir):
    # when
    context = {
        "name": "DSC 40B",
        "instructor": "Justin Eldridge",
        "presentations": ["lectures", "discussions"],
    }
    with (tempdir / "course.yaml").open("w") as fileobj:
        yaml.dump(context, fileobj)

    instantiate.cli(
        [str(TEMPLATE_2_PATH), "bar", "--context", "course.yaml"], cwd=tempdir
    )

    # then
    with (tempdir / "bar" / "one").open() as fileobj:
        contents = fileobj.read()

    assert contents.strip() == "Justin Eldridge is the instructor of DSC 40B. lectures"


def test_numbering(tempdir):
    # when
    instantiate.cli([str(TEMPLATE_1_PATH), "foo", "--numbering", "3"], cwd=tempdir)

    # then
    assert (tempdir / "001-foo").is_dir()


def test_no_numbering(tempdir):
    # when
    instantiate.cli([str(TEMPLATE_1_PATH), "foo"], cwd=tempdir)

    # then
    assert (tempdir / "foo").is_dir()


def test_raise_valueerror_if_template_dne():
    with raises(ValueError):
        instantiate.cli(["dne", "there"])
