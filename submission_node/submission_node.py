import fxt.tools.submit_to_farm.job.jobs as deadline_jobs
import fxt.tools.submit_to_farm.job.job_builder as job_gen
import fxt.tools.submit_to_farm.job.job_errors as job_error
import fxt.tools.submit_to_farm.submission_node.submission_node_error as submission_error
import hou
import copy
from attr import attrs, attrib


@attrs
class SubmitNodeStatus(object):
    """
    Essential data for navigating through the Houdini ROP network
    """
    dependents = attrib(factory=list)

    node = attrib(type=hou.Node, default=None)
    name = attrib(type=str, default="Submit Node")
    path = attrib(type=str, default="")
    # input submit node (this job depends on them
    inputs = attrib(type=list, default=[])
    # bypass flag enabled, don't submit and affect attribute transfer parenting
    bypass = attrib(type=bool, default=False)
    supported = attrib(type=bool, default=True)
    valid = attrib(type=bool, default=True)
    job_ids = attrib(factory=list)
    jobs = attrib(factory=list)
    # inherit job attributes from parent such as submit to farm
    parent_job = attrib(factory=deadline_jobs.HoudiniDeadlineJobInfo)
    # for recursive node like fetch
    redirect_node = attrib(type=hou.Node, default=None)


class SubmitNode(SubmitNodeStatus):
    """
    Represent a task to be submitted to deadline
    """
    def __init__(self, node):
        super(SubmitNode, self).__init__()

    def __repr__(self):
        return self.node.name()

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return self.path != other.path

    def update(self):
        return NotImplementedError

    def _update_job(self):
        return NotImplementedError

    def check(self):
        """=
        :return: True f it's ready for submit
        """
        exceptions = []
        # bypassed node
        if self.bypass:
            return False

        if self.valid is False:
            return False

        # utility node
        if self.jobs is None:
            return False

        if len(self.jobs) < 1:
            return False

        return True


class RopNode(SubmitNode):
    """
    standard rop node like mantra and alembic
    """
    def __init__(self, node):
        super(RopNode, self).__init__(node)

    def update(self):
        super(RopNode, self).update()
        self._update_job()

    def _update_job(self):
        if not self.bypass:
            job = job_gen.HoudiniDeadlineJobBuild(self.node, parent_job=self.parent_job)
            if job is None:
                self.valid = False
                self.supported = False
            else:
                job.node_name = self.name
                self.jobs.append(job)
        else:
            if self.parent_job:
                reference_job = copy.copy(self.parent_job)
                reference_job.submittable = False
                self.jobs.append(self.reference_job)



class MergeNode(SubmitNode):
    def __init__(self, node):
        super(MergeNode, self).__init__(node)
        pass

    def update(self):
        super(MergeNode, self).update()
        self._update_job()

    # copy job from parents
    def _update_job(self):
        reference_job = copy.copy(self.parent_job)
        reference_job.submittable = False
        self.jobs.append(reference_job)


class NullNode(SubmitNode):
    def __init__(self, node):
        super(NullNode, self).__init__(node)
        pass

    def update(self):
        super(NullNode, self).update()
        self._update_job()

    def _update_job(self):
        reference_job = copy.copy(self.parent_job)
        reference_job.submittable = False
        self.jobs.append(reference_job)


class SwitchNode(SubmitNode):
    def __init__(self, node):
        super(SwitchNode, self).__init__(node)

    def update(self):
        super(SwitchNode, self).update()
        self._update_input()
        self._update_input()

    def _update_input(self):
        if self.bypass is False:
            choice = self.node.parm("index").eval()
            inputs = [self.node.inputs()[choice]]
        else:
            inputs = self.node.inputs()
        self.inputs = inputs

    def _update_job(self):
        reference_job = copy.copy(self.parent_job)
        reference_job.submittable = False
        self.jobs.append(reference_job)

class FetchNode(SubmitNode):
    def __init__(self, node):
        super(FetchNode, self).__init__(node)
        # check if fetch node is pointing to another submission node
        if not node.isBypassed():
            if node:
                source = node.parm("source").eval()
                if source:
                    source_node = hou.node(source)
                    # build as submission node when source node is in ROP
                    if source_node.type().category().name() == "Driver":
                        self.redirect_node = source_node
                else:
                    raise submission_error.SourceNotFoundError("Error initializing Fetch Node", node)

    def update(self):
        super(FetchNode, self).update()
        self._update_job()

    def _update_job(self):
        if self.bypass:
            reference_job = copy.copy(self.parent_job)
            reference_job.submittable = False
            self.jobs.append(reference_job)
        else:
            source = self.node.parm("source").eval()
            if source:
                source_node = hou.node(source)
                # build as submission node when source node is in ROP
                # Build inherit job properties from parent node, for redirected nodes to copy
                if source_node.type().category().name() == "Driver":
                    job = job_gen.HoudiniDeadlineJobBuild(self.node, parent_job=self.parent_job)
                    self.jobs.append(job)
                    pass

                elif source_node.type().category().name() == "Sop":
                    source_job = job_gen.HoudiniDeadlineJobBuild(self.node, parent_job=self.parent_job)
                    job = job_gen.HoudiniDeadlineJobBuild(source_node, parent_job=source_job)

                    if job is None:
                        self.valid = False
                        self.supported = False
                        raise submission_error.NodeNotFoundError("No sop jobs")
                    else:
                        job.node_name = self.name
                        self.jobs.append(job)
                        pass

                else:
                    print " network type not supported"
                    self.valid = False
                    self.supported = False
                    pass
            else:
                self.bypass = True


class SubnetNode(SubmitNode):
    # TODO: not supported yet
    def __init__(self, node):
        raise NotImplementedError
        super(SubnetNode, self).__init__(node)
        pass

    def inputs(self):
        """
        go inside subnet and select all end nodes
        Only the selected
        :return:
        """
        raise NotImplementedError
        return self.node.inputs()


class HQSimNode(SubmitNode):
    """
        HQ Sim node for distributed simulation
    """
    def __init__(self, node):
        super(HQSimNode, self).__init__(node)

    def update(self):
        super(HQSimNode, self).update()
        self._update_job()

    def _update_job(self):
        if self.bypass:
            reference_job = copy.copy(self.parent_job)
            reference_job.submittable = False
            self.jobs.append(reference_job)
        else:
            source = self.node.parm("hq_driver").eval()
            if source is None:
                raise submission_error.SourceNotFoundError("Error Setting up Job", self.node)

            source_node = hou.node(source)
            if source_node is None:
                self.valid = False
                return

            source_job = job_gen.HoudiniDeadlineJobBuild(source_node, parent_job=self.parent_job)
            if source_job is None:
                self.valid = False
                return

            job = deadline_jobs.HoudiniHqRenderDeadlineJob(self.node, source_job=source_job)

            if job is None:
                self.valid = False
                self.supported = False
                return

            job_gen.job_from_parent(job, self.parent_job)
            job_gen.job_from_hou_node(job, self.node)
            job.node_name = self.name
            job.update()
            self.jobs.append(job)


class WedgeNode(SubmitNode):
    """
    For Wedging node
    """
    def __init__(self, node):
        super(WedgeNode, self).__init__(node)
        self.num_of_wedges = 0

    def update(self):
        super(WedgeNode, self).update()
        self._get_num_of_wedges()
        self._update_job()

    def _get_num_of_wedges(self):
        self.num_of_wedges = self.node.parm("steps1").eval()
        pass

    def _update_job(self):
        if self.bypass:
            reference_job = copy.copy(self.parent_job)
            reference_job.submittable = False
            self.jobs.append(reference_job)
        else:
            source = self.node.parm("driver").eval()
            if source is None:
                self.bypass = True
                return

            source_node = hou.node(source)
            if source_node is None:
                self.valid = False
                return
            # source job is the job of regular sim attributes
            source_job = job_gen.HoudiniDeadlineJobBuild(source_node, parent_job=self.parent_job)
            if source_job is None:
                self.valid = False
                return

            # calculate wedge number and duplicate jobs with different wedge number
            for w in range(self.num_of_wedges):
                # job is specific for wedging
                job = deadline_jobs.HoudiniWedgeDeadlineJob(self.node, source_job=source_job, wedge_num=w)
                if job is None:
                    continue
                else:
                    job_gen.job_from_parent(job, self.parent_job)
                    job_gen.job_from_hou_node(job, self.node)
                    # used wedge node name instead
                    job.node_name = self.name
                    job.update()
                    self.jobs.append(job)

            if len(self.jobs) <1:
                self.valid = False
                self.supported = False
                return


