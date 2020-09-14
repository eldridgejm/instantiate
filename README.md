instantiate
===========

A simple tool to create new project directories from templates.

Usage
-----

```shell
> instantiate path_to_template project_name --numbering 2 --context my_variables.yaml
```

This will:

- infer the current project number from the projects currently in the directory
- create a new directory named `##-project_name`, where `##` is the current
  project number zero-padded to two places. 
- copy the entire contents of the `path_to_template` directory into the project
- perform substitutions in every copied file using Jinja2 and variables read
  from the `my_variables.yaml` file

For instance, if the `vars.yaml` file looks like this:

```yaml
name: Justin
course: DSC 40B
year: 2020
```

Then the variables are accessible as `{{ my_variables.name }}`, `{{
my_variables.course }}`, and `{{ my_variables.year }}`, respectively.

Several variables are generated automatically. They are:

- `{{ project.name }}`: the project name passed on the command line
- `{{ project.number }}`: the number of the current project