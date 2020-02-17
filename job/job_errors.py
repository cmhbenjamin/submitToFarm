import jobs as dl_job


class JobError(Exception):
    def __init__(self, message, job):
        super(JobError, self).__init__(message)
        self.job = job

    def __str__(self):
        return "Job error{} \n at node: {}:\n {}\n".format(self.__class__.__name__, self.job.node, self.message)


class NodeNotFoundError(JobError):
    def __init__(self, message, job):
        super(NodeNotFoundError, self).__init__(message, job)


class NodeNotSupported(Exception):
    def __init__(self, message, node):
        super(NodeNotSupported, self).__init__(message)
        self.node = node

    def __str__(self):
        return "{} Error: \n at node: {}:\n {}\n".format(self.__class__.__name__, self.node, self.message)


class NodeDefinitionNotMatching(Exception):
    def __init__(self, message, node):
        super(NodeDefinitionNotMatching, self).__init__(message)
        self.node = node

    def __str__(self):
        return "{} Error: \n at node: {}:\n {}\n".format(self.__class__.__name__, self.node, self.message)

#node not supported

#