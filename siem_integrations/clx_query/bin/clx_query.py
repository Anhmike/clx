# Copyright (c) 2020, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import re
import sys, requests, json
from splunklib.searchcommands import (
    dispatch,
    GeneratingCommand,
    Configuration,
    Option,
    validators,
)
import splunklib.client as client

log = logging.getLogger(__name__)

REGEX_PATTERN = r"([LIMIT|limit]+.[0-9]+$)"

@Configuration()
class ClxQuery(GeneratingCommand):
    query = Option(require=True)

    def generate(self):
        configs = client.Configurations(self.service)
        for config in configs:
            if config.name == "clx_query_setup":
                clx_config = config.iter().next().content

        url = self.construct_url(clx_config, self.query)
        response = requests.get(url)

        if response.status_code != 200:
            yield {"ERROR": response.content}
        else:
            results = json.loads(json.loads(response.content))
            for result in results:
                yield result

    def construct_url(self, config, query):
        base_url = "http://%s:%s/clxquery" % (
            config["clx_hostname"],
            config["clx_port"],
        )
        url = base_url + "/" + query
        has_query_limit = re.findall(REGEX_PATTERN, query)
        
        if has_query_limit:
           return url
        if config["clx_query_limit"]:
            url = "%s LIMIT %s" %(url, config["clx_query_limit"])
        
        return url


dispatch(ClxQuery, sys.argv, sys.stdin, sys.stdout, __name__)
