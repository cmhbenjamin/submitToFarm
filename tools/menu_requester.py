
import time
import requests


class menu_requester(object):
    """
    This class fix the problem when Houdini sending multiple request to menu script when updated
    This buffers the request to server, reduce frequent request by storing recent returns from command
    """

    # stores latest request with its request time
    recent_request = dict()

    def __init__(self, address, refresh_time=10, timeout=1):
        super(menu_requester, self).__init__()
        #limit to submit every x seconds
        self.refresh_time = refresh_time
        self.timeout = timeout
        self.address = address

    def _query(self, cmd, **kwargs):
        """
        Submit request to server through request
        Args:
            cmd: command to be submit, for example: pools, groups
            **kwargs:

        Returns:

        """
        rep = requests.get(self.address + '/' + cmd, params=kwargs, timeout=self.timeout)
        if rep.status_code == requests.codes.ok:
            if rep.json() and len(rep.json()) >= 1:
                return rep.json()
        else:
            rep.raise_for_status()

    def submit(self, query, **kwargs):
        """
        Look up to see if the query is stored in the recent_request first
        If not, submit the query and store the result in recent_request
        :param query:
        :param kwargs:
        :return:
        """
        curr_time = time.time()
        last_submit_time = -1
        if (query in menu_requester.recent_request.keys()):
            last_submit_time = menu_requester.recent_request[query]["time"]
        else:
            menu_requester.recent_request[query] = dict()
            menu_requester.recent_request[query]["time"] = curr_time
        if curr_time - last_submit_time > self.refresh_time:
            query_result = self._query(query, **kwargs)
            menu_requester.recent_request[query]["result"] = query_result
            menu_requester.recent_request[query]["time"] = curr_time
            return query_result
        else:
            return menu_requester.recent_request[query]["result"]