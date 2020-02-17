import fxt.tools.common.deadline.bc_deadline as deadline
import fxt.tools.submit_to_farm.submission_node.submission_tree as tree
import error as error

def submit_to_farm(node):
    """
    Initialize server, build submission tree, submit tree
    Args:
        node: Node to submit, usually is the Submission_to_farm node

    Returns: submitted jobs

    """
    address = 'http://pidge:8082/api'
    try:
        server = deadline.DeadlineServer(address)
    except Exception as e:
        raise error.SubmitToFarmServerError(str(e))

    try:
        root = tree.create_submission_tree(node)
    except Exception as e:
        raise error.SubmitToFarmBuildError(str(e))

    try:
        tree.submit_tree(root, server)
    except Exception as e:
        raise error.SubmitToFarmSubmitError(str(e))

    return server.submitted


def submit_single_node(node):
    """
    Not working yet, need to figure out ways to find the deadline job attributes
    :param node: Houdini node
    :return: submitted jobs
    """
    raise NotImplementedError
    address = 'http://pidge:8082/api'
    server = deadline.DeadlineServer(address)
    root = tree.create_submission_tree(node)
    tree.submit_tree(root, server)
    return server.submitted


def test_submit_to_farm(node):
    server = deadline.TestDeadlineServer()
    root = tree.create_submission_tree(node)
    tree.submit_tree(root, server)
    return server.submitted