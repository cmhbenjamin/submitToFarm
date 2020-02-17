from attr import attrs, attrib
#python 3
#import typing
import six
import fxt.tools.common.bc_core as core
import fxt.tools.submit_to_farm.job.job_helper as helper
from fxt.tools.common.deadline.bc_deadline_job import DeadlineJobInfo
import job_errors as error
from attr import attrs, attrib


#TODO: remove defualt values to detect error when attribute not actually set

@attrs
class HoudiniDeadlineJobInfo(DeadlineJobInfo):
    """
    This is a class for representing deadline job data for Houdini jobs
    Apart from default deadline info, this got more info for plugin info like output driver
    """
    output_driver = attrib(type=six.string_types, default='/out')
    houdini_job = attrib(type=six.string_types, default=r'T:/dwtv/hub/Fx')
    build = attrib(type=six.string_types, default='64bit')
    version = attrib(type=six.string_types, default='17.0')

    def output(self):
        parent_output = super(HoudiniDeadlineJobInfo, self).output()
        output = {'PluginInfo': {
                    'SceneFile': self.scene_path,
                    'OutputDriver': self.output_driver,
                    'Version': self.version,
                    'HoudiniHipDw': self.scene_path,
                    'HoudiniJobDw': self.houdini_job,
                    'Build': self.build
                    }
                }
        parent_output['PluginInfo'] = output['PluginInfo']
        return parent_output


class HoudiniDeadlineJob(HoudiniDeadlineJobInfo):
    def get_output_path(self):
        raise NotImplementedError

    def _update_output_path(self):
        """
        get output file name without the frame number
        :return:
        """
        output_parm = self.get_output_path()
        if output_parm:
            self.output_path = helper.convert_dl_output_path(output_parm.eval())

    def get_frame_range(self):
        if self.node.parm("trange") and self.node.parm("trange").eval() == 0:
            start = 1
            end = 1
            step = 1
        else:
            start = self.node.parm('f1').eval()
            end = self.node.parm('f2').eval()
            step = self.node.parm('f3').eval()
        return start, end, step

    def _update_frame_range(self):
        if self.override_frame_range:
            # use parent frame range
            pass
        else:
            # user local frame range
            frame_range = self.get_frame_range()
            if frame_range:
                self.frame_range = frame_range

    def get_chunk_size(self):
        raise NotImplementedError

    def _update_chunk_size(self):
        extra_parm = self.node.parm("dl_chunk_size")
        if extra_parm and not extra_parm.isDisabled():
            # use node chunk_size
            pass
        else:
            # use chunk_size from parent
            chunk_size = self.get_chunk_size()
            if chunk_size:
                self.chunk_size = chunk_size


    def update(self):
        # set all default info
        # set output path
        self._update_output_path()

        # see if chunk size is overwritten by the node
        self._update_chunk_size()

        # see if frame range is overwritten by the submit node
        # frame range
        self._update_frame_range()

        #update node name

    def __init__(self, node):
        super(HoudiniDeadlineJob, self).__init__()
        self.node = node

        # output driver
        self.output_driver = self.node.path()


class HoudiniDwtvSubmitToFarmDeadlineJob(HoudiniDeadlineJob):
    def __init__(self, node):
        super(HoudiniDwtvSubmitToFarmDeadlineJob,self).__init__(node)
        self.initialized = True
        self.submittable = False
        # collect attributes from node

    def _update_frame_range(self):
        if self.node.parm("dl_override_frame_range"):
            # update frame range from node
            self.frame_range = self.get_frame_range()
        else:
            # user parent's range
            pass

    def get_output_path(self):
        return None

    def get_chunk_size(self):
        return None


# #############
# # Render
# #############


class HoudiniMantraDeadlineJob(HoudiniDeadlineJob):
    def __init__(self, node):
        super(HoudiniMantraDeadlineJob,self).__init__(node)
        self.submittable = True

    def get_output_path(self):
        return self.node.parm("vm_picture")

    def get_chunk_size(self):
        return self.chunk_size_static


class HoudiniVRayRendererDeadlineJob(HoudiniDeadlineJob):
    def __init__(self, node):
        super(HoudiniVRayRendererDeadlineJob,self).__init__(node)
        self.submittable = True

    def get_output_path(self):
        return self.node.parm("picture")

    def get_chunk_size(self):
        return self.chunk_size_static


class HoudiniOpenglDeadlineJob(HoudiniDeadlineJob):
    def __init__(self, node):
        super(HoudiniOpenglDeadlineJob,self).__init__(node)
        self.submittable = True

    def get_output_path(self):
        return self.node.parm("picture")

    def get_chunk_size(self):
        return self.chunk_size_static

# #############
# # Cache
# #############


class HoudiniRopGeometryDeadlineJob(HoudiniDeadlineJob):
    def __init__(self, node):
        super(HoudiniRopGeometryDeadlineJob,self).__init__(node)
        self.submittable = True

    def get_output_path(self):
        return self.node.parm("sopoutput")

    def get_chunk_size(self):
        return self.chunk_size_dynamic


# rop dop
class HoudiniRopDopDeadelineJob(HoudiniDeadlineJob):
    pass


class HoudiniRopAlembicDeadlineJob(HoudiniDeadlineJob):
    def __init__(self, node):
        super(HoudiniRopAlembicDeadlineJob,self).__init__(node)
        self.submittable = True

    def get_output_path(self):
        return self.node.parm("filename")

    def get_chunk_size(self):
        return self.chunk_size_dynamic


class HoudiniRopFbxDeadlineJob(HoudiniDeadlineJob):
    pass

class HoudiniFetchJob(HoudiniDeadlineJob):
    def __init__(self, node):
        super(HoudiniFetchJob, self).__init__(node)
        self.submittable = True

    def get_frame_range(self):
        return None

    def get_output_path(self):
        return None

    def get_chunk_size(self):
        return None

class HoudiniFileCacheDeadlineJob(HoudiniDeadlineJob):
    def __init__(self, node):
        super(HoudiniFileCacheDeadlineJob, self).__init__(node)
        self.submittable = True
        render_node = self.node.node("render")
        if render_node:
            self.output_driver = render_node.path()
        else:
            raise error.NodeDefinitionNotMatching("Cache File Node definition changed, please update source code", node)

    def get_output_path(self):
        return self.node.parm("file")

    def get_chunk_size(self):
        return self.chunk_size_dynamic

    def get_frame_range(self):
        driver = self.node.node('render')
        if driver.parm("trange") and driver.parm("trange").eval() == 0:
            # get value at frame 1
            start = 1
            end = 1
            step = 1
        else:
            start = driver.parm('f1').eval()
            end = driver.parm('f2').eval()
            step = driver.parm('f3').eval()
        return start, end, step

# #############
# # Sim
# #############


class HoudiniHqRenderDeadlineJob(HoudiniDeadlineJob):
    def __init__(self, node, source_job=None):
        super(HoudiniHqRenderDeadlineJob, self).__init__(node)
        self.submittable = True
        self.source_job = source_job
        self.sim_job = True
        self.sim_requires_tracking = True


    def set_source_job(self, source_job):
        self.source_job = source_job


    def get_frame_range(self):
        """
        Wedge number is represent in frame range
        :return:
        """
        start = 0
        end = self.node.parm("num_slices").eval()-1
        step = 1
        return start, end, step

    def get_output_path(self):
        # need to be handled in other job
        if self.source_job:
            return self.source_job.get_output_path()
        else:
            raise error.NodeNotFoundError("No driver found", self)

    def get_chunk_size(self):
        return None

    def output(self):
        parent_output = super(HoudiniHqRenderDeadlineJob, self).output()
        # can't have chunk size in the attribute
        del parent_output['JobInfo']['ChunkSize']
        output = {'PluginInfo': {
                        "SimJob": self.sim_job,
                        "SimRequiresTracking": self.sim_requires_tracking
                    }
                 }
        core.dict_merge(parent_output, output)
        return parent_output


class HoudiniWedgeDeadlineJob(HoudiniDeadlineJob):
    def __init__(self, node, source_job=None, wedge_num=-1):
        super(HoudiniWedgeDeadlineJob, self).__init__(node)
        self.submittable = True
        self.source_job = source_job
        self.sim_job = False
        self.wedge_num = wedge_num


    def set_source_job(self, source_job):
        self.source_job = source_job

    def get_frame_range(self):
        # need to be handled in other job
        if self.source_job:
            return self.source_job.frame_range
        else:
            return None

    # TODO: raise an error earlier in the pipe so that we can raise an error with the path as well
    def get_output_path(self):
        # need to be handled in other job
        if self.source_job:
            return self.source_job.get_output_path()
        else:
            raise error.NodeNotFoundError("No driver found", self)

    def get_chunk_size(self):
        if self.source_job:
            return self.source_job.get_chunk_size()
        else:
            raise error.NodeNotFoundError("No driver found", self)

    def output(self):
        parent_output = super(HoudiniWedgeDeadlineJob, self).output()
        # can't have chunk size in the attribute
        output = {'PluginInfo': {
                        "wedgeNum": self.wedge_num
                    }
                 }
        core.dict_merge(parent_output, output)
        return parent_output

# #############
# # Other
# #############
#
# class BaketextureDeadlineJob(HoudiniDeadlinePluginInfo, HoudiniDeadlineJobInfo):
#     pass
#
# class CompositeDeadlineJob(HoudiniDeadlinePluginInfo, HoudiniDeadlineJobInfo):
#     pass
