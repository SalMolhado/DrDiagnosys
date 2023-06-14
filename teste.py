from os import path, listdir, getcwd

assets_directory = path.join(getcwd(), "Assets\\nome e desc")
contents = listdir(assets_directory)

manipulation_directory = path.join(getcwd(), 'Data\\Manipulation\\nome e desc')
inserts = listdir(manipulation_directory)

for insert, content in zip(inserts, contents):
    print(insert, content)