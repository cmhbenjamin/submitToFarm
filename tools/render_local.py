import fxt.tools.submit_to_farm.job.job_builder as job_builder
def render_local(node):
    """
        frame range from node
    """
    node.parm("execute").pressButton()


def start_local(node):
    rendered = {}
    childrenList = [c for c in node.inputs() if c is not None]
    for c in childrenList:
        newRend = walk_node_local(c, rendered)
        rendered.update(newRend)


def walk_node_local(node, rendered):
    if node is not None:

        if node.path() not in rendered.keys():
            childrenList = [c for c in node.inputs() if c is not None]
            for c in childrenList:
                newRend = walk_node_local(c, rendered)
                rendered.update(newRend)

            render_local(node)
            rendered[node.path()] = 1

    else:
        print "error at node {}".format(node.name())

    return rendered
