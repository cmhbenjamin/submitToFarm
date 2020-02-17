import fxt.tools.submit_to_farm.submission_node.submission_node as sub
import fxt.tools.submit_to_farm.submission_node.submission_node_error as submission_node_error

def SubmitNodeGen(hou_node, parent_node=None):
    """
    Generator class to generate submission_node object from houdini node
    Submission_node object is used in Submission Tree building later
    Args:
        hou_node: Houdini Rop node to submit
        parent_node: Parent of Rop node

    Returns:
        submission_node
    """

    def find_class(node):
        """
         Find the class for each Rop node support
           #     :param node: Houdini Rop node
           #     :return: Submission Node class
           #
        """
        node_type = node.type().nameComponents()[2]

        if node_type == "merge":
            return sub.MergeNode

        if node_type == "null":
            return sub.NullNode

        if node_type == "switch":
            return sub.SwitchNode

        if node_type == "fetch":
            return sub.FetchNode

        if node_type == "subnet":
            return sub.SubmitNode

        if node_type == "hq_sim":
            return sub.HQSimNode

        if node_type == "wedge":
            return sub.WedgeNode

        if node_type == "dwtv_submit_to_farm":
            return sub.RopNode

        if node_type == "ifd":
            return sub.RopNode

        if node_type == "vray_renderer":
            return sub.RopNode

        return sub.RopNode


    def initiate_submit_node(submit_node, hou_node, parent_node=None):
        """
        Initialize values of submission_node object
        Args:
            submit_node:
            hou_node:
            parent_node:

        Returns:

        """
        submit_node.node = hou_node
        submit_node.dependents = list()
        submit_node.name = hou_node.name()
        submit_node.path = hou_node.path()
        submit_node.inputs = hou_node.inputs()
        submit_node.bypass = hou_node.isBypassed()
        if parent_node:
            if len(parent_node.jobs) >= 1:
                submit_node.parent_job = parent_node.jobs[0]

    if hou_node is None:
        raise submission_node_error.NodeNotFoundError("node not found")

    node_class = find_class(hou_node)
    if node_class is None:
        raise submission_node_error.NodeTypeNotSupportedError("node type {} of {} not supported".format(hou_node.type().nameComponents()[2], hou_node))

    try:
        rop_node = node_class(hou_node)
    except Exception as e:
        raise submission_node_error.SubmissionNodeError(str(e), hou_node)

    # handle nodes that redirect the flow like fetch and wedge:
    initiate_submit_node(rop_node, hou_node, parent_node=parent_node)
    rop_node.update()
    #
    if rop_node.redirect_node:
        sub_node = SubmitNodeGen(rop_node.redirect_node, parent_node=rop_node)
        rop_node.jobs = sub_node.jobs

    return rop_node
