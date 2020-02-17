
class SubmissionNodeError(Exception):
    def __init__(self, message, submission_node):
        super(SubmissionNodeError, self).__init__(message)

        self.submission_node = submission_node

    def __str__(self):
        return "Job error{} \n at node: {}:\n {}\n".format(self.__class__.__name__, self.submission_node.node, self.message)


class ValidationError(Exception):
    def __init__(self, message, errors):
        super(ValidationError, self).__init__(message)
        self.errors = errors


class NodeNotFoundError(Exception):
    """
    Node can't be located
    """
    def __init__(self, message):
        super(NodeNotFoundError, self).__init__(message)


class SourceNotFoundError(Exception):
    """
    Node requires source not found
    """
    def __init__(self, message, node):
        super(SourceNotFoundError, self).__init__(message)
        self.node = node

    def __str__(self):
        return "{} Error \n at node: {}:\n {}\n".format(self.__class__.__name__, self.node, self.message)


class NodeTypeNotSupportedError(Exception):
    """
    Unsupported node class
    """
    def __init__(self, message):
        super(NodeTypeNotSupportedError, self).__init__(message)


class SubmissionNodeInvalidError(SubmissionNodeError):
    """
    Submission node
    """
    def __init__(self, message, submission_node):
        super(SubmissionNodeError, self).__init__(message, submission_node)
