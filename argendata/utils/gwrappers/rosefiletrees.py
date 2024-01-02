def traverse_nodes(dct, sb, padding, pointer, has_right_sibling, show):
    sb.append("\n" + padding + pointer + str(show(dct)))

    padding_builder = padding + ("│  " if has_right_sibling else "   ")
    padding_for_both = padding_builder

    if 'resources' in dct:
        resources = dct['resources']
        if 'files' in resources and resources['files']:
            files = resources['files'][::-1]
            for file in files[:-1]:
                traverse_nodes(file, sb, padding_for_both, "├──", True, show=show)
            else:
                traverse_nodes(files[-1], sb, padding_for_both, '├──' if resources['folders'] else '└──', False, show=show)

        if 'folders' in resources and resources['folders']:
            folders = resources['folders'][::-1]
            for folder in folders[:-1]:
                traverse_nodes(folder, sb, padding_for_both, "├──", True, show=show)
            else:
                traverse_nodes(folders[-1], sb, padding_for_both, "└──", False, show=show)


def traverse_pre_order(dct, show=lambda x: x['id']):
    result_sb = [str(show(dct))]

    if 'resources' in dct:
        resources = dct['resources']
        if 'files' in resources and resources['files']:
            files = resources['files'][::-1]
            for file in files[:-1]:
                traverse_nodes(file, result_sb, "", "├──", True, show=show)
            else:
                traverse_nodes(files[-1], result_sb, "", '├──' if resources['folders'] else '└──', False, show=show)

        if 'folders' in resources and resources['folders']:
            folders = resources['folders'][::-1]
            for folder in folders[:-1]:
                traverse_nodes(folder, result_sb, "", "├──", True, show=show)
            else:
                traverse_nodes(folders[-1], result_sb, "", "└──", False, show=show)

    return "".join(result_sb)
