def removeSuffix(name):
    """
    Remove suffix from given name string
    :param name: given name string to process
    :return: str, name without suffix
    """

    edits = name.split('_')

    if len(edits) < 2:
        return name

    suffix = '_' + edits[-1]
    nameNoSuffix = name[:-len(suffix)]

    return nameNoSuffix


def removeNodeAttr(name):
    """
    remove attr from given string
    :param name: str, string
    :return: str, pure node name
    """
    edit = name.split('.')

    if len(edit) < 2:
        return edit
    Attr = '.' + edit[-1]

    meshName = name[:-len(Attr)]

    return meshName


def getPureVertex(name):
    edit = name.split('.')

    if len(edit) < 2:
        return edit

    meshName = edit[0] + '.'

    pureVertex = name[len(meshName):]

    return pureVertex
