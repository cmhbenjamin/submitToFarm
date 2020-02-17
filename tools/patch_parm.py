import hou
"""
    Helps copying parameter between nodes if it doesn't exist
"""

def copy_parms(to_node, from_node):
    """
        copy parms from from_node to to_node
    """
    parms = from_node.parmTemplateGroup().entries()
    user_parm_source = [p.name() for p in from_node.spareParms()]
    user_parm_dest = [p.name() for p in to_node.spareParms()]
    ptg = to_node.parmTemplateGroup()
    for p in parms:
        if p.name() in user_parm_source and p.name() not in user_parm_dest:
            ptg.insertBefore(ptg.entries()[0], p)
    to_node.setParmTemplateGroup(ptg)


def remove_parms(to_node, from_node):
    """
        remove parms in to_node that exists in from_node
    """
    ptg = to_node.parmTemplateGroup()
    user_parm_source = [p.name() for p in from_node.spareParms()]
    for p in ptg.entries():
        if p.name() in user_parm_source:
            ptg.remove(p)
    to_node.setParmTemplateGroup(ptg)



