import hou
import submit
import fxt.tools.submit_to_farm.tools.patch_parm as patch
import error as error
"""
    Called by functions in HDA
"""

def submit_callback(**kwargs):
    """
    Callback for HDA's submit button
    :param kwargs: Submission Node
    :return:
    """
    if hou.hipFile.hasUnsavedChanges():
        if hou.ui.displayMessage(
                "The scene has unsaved changes and must be saved before the job can be submitted.\nDo you wish to "
                "save?",
                buttons=("Yes", "No"), title="Submit Houdini To Deadline") == 0:
            hou.hipFile.save()
        else:
            return
    try:
        result = submit.submit_to_farm(kwargs["node"])
        display = [r['Props']['Name'] for r in result.values()]
        hou.ui.displayMessage('Submitted Jobs: {}'.format(str(display)))
        print result
    except error.SubmitToFarmServerError as e:
        hou.ui.displayMessage('error when setting up server connection:\n{}'.format(str(e)))
    except error.SubmitToFarmBuildError as e:
        hou.ui.displayMessage('error when building the dependency tree:\n{}'.format(str(e)))
    except error.SubmitToFarmSubmitError as e:
        hou.ui.displayMessage('error at submission:\n{}'.format(str(e)))



def submit_test_callback(**kwargs):
    print submit.test_submit_to_farm(kwargs['node'])


def submit_local_callback():
    pass

def patch_nodes_callback(**kwargs):
    patch_ancestors(kwargs['node'])

def unpatch_nodes_callback(**kwargs):
    patch_ancestors(kwargs['node'], unpatch=True)

def patch_ancestors(node, unpatch=False):
    """
    copy parameter from a null node inside hda to all nodes connect to the hda
    :param node: root node
    :param unpatch:
    """
    interface = hou.node("./extra_interface")
    nodes = node.inputAncestors()
    for n in nodes:
        if not unpatch:
            patch.copy_parms(n, interface)
        else:
            patch.remove_parms(n, interface)