instantiate
===========

A simple tool to create new project directories from templates.

Usage
-----

```shell
> instantiate path_to_template project_name --numbering 2 --context my_variables.yaml
```

This will:

- infer the current project number from the projects in the current directory
- create a directory named `##-project_name`, where `##` is the newest
  project number zero-padded to two places
- copy the entire contents of the `path_to_template` directory into the project
- perform substitutions in every copied file using Jinja2 and variables read
  from the `my_variables.yaml` file

For instance, if the `my_variables.yaml` file looks like this:

```yaml
name: Justin
course: DSC 40B
year: 2020
```

Then the variables are accessible as `{{ my_variables.name }}`, `{{
my_variables.course }}`, and `{{ my_variables.year }}`, respectively. In general,
if your context file is named `foo.yaml`, your variables are accessible as `{{ foo.<whatever> }}`.

Several variables are generated automatically. They are:

- `{{ project.name }}`: the project name passed on the command line
- `{{ project.number }}`: the number of the current project
