<!-- This is a Markdown file and is best viewed with a suitable program such as Okular -->

When you have compiled the program using the
[build instructions](../src/README.md),
you can run it from the
[src folder](../src)
without arguments to use the default configuration.
Alternatively you can specify two command-line arguments: the configuration file path and the output folder path.
```
./planetary-motion /path/to/config.txt /path/to/output_folder
```

The program can also be directly run from the Python script to get the advanced plotting functionality.
The Python script will also take care of the compilation, provided that you have installed all
the necessary libraries.
```
python3 main.py
```

The first line of the configuration file should be `planetary-motion configuration`.
There should be two sections: `[scalars]` and `[arrays]`.
Scalars should be specified by `name = value` and arrays should have their names on separate rows
with data directly on the following rows.
Empty lines and lines starting with # and ; are ignored.
Please see the example [config.txt](./config.txt) in this folder for a detailed listing of the parameters.

<!-- By the way, in my opinion it would be the best to put both build and usage
documentation in one README file in the root of the repository, since
this is a rather small project. -->
