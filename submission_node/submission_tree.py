import fxt.tools.submit_to_farm.submission_node.submission_node_builder as submit_node_gen
import fxt.tools.submit_to_farm.submission_node.submission_node_error as submission_node_error


def create_submission_tree(submit_node, parent_node=None):
    """
    Recursively go through all the dependents in the tree with depth first
    Then store all it's child's dependency so
    parent's dependency have all child node
    :param node: houdini node
    :param parent: parent submit node
    :return: the root submission node
    """

    curr_submit_node = submit_node_gen.SubmitNodeGen(submit_node, parent_node=parent_node)
    inputs = curr_submit_node.inputs
    for i in inputs:
        child_node = create_submission_tree(i, parent_node=curr_submit_node)
        dependents = list(child_node.dependents)
        dependents.append(child_node)
        for c in dependents:
            if c not in curr_submit_node.dependents:
                curr_submit_node.dependents.append(c)

    return curr_submit_node


def fix_duplicated_dependency(submit_node):
    """
    Remove duplication that happens when 2 nodes have the same parent
    :param submit_node:
    :return:
    """
    node_list = submit_node.dependents
    for n in node_list:
        for i, c in enumerate(n.dependents):
            if c in node_list:
                n.dependents[i] = node_list[node_list.index(c)]


def submit_tree(submit_node, server):
    """
    Go through the submission tree and submit jobs in submission node
    Stores job id so it could be used as dependency
    :param submit_node:
    :param server:
    :return:
    """
    fix_duplicated_dependency(submit_node)
    submit_node_list = submit_node.dependents
    for s in submit_node_list:
        if s.check():
            dependencies = s.dependents
            dependent_job_ids = list()
            for d in dependencies:
                dependent_job_ids.extend(d.job_ids)
            for j in s.jobs:
                if j.submittable:
                    if j.check():
                        j.dependencies = dependent_job_ids
                        s.job_ids.append(server.submit_job(j.output()))
                    else:
                        raise submission_node_error.SubmissionNodeInvalidError(j, s)
