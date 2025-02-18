#!/usr/bin/env python
# Copyright (c) Alexey Zasimov <zasimov@gmail.com>
# Copyright (c) Eugene Frolov <eugene@frolov.net.ru>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging


class CorrelationLoggerAdapter(logging.LoggerAdapter):
    """It writes correlation id for each log entry"""

    def __init__(self, logger, correlation_id):
        super(CorrelationLoggerAdapter, self).__init__(logger, {})
        self._correlation_id = correlation_id

    def process(self, msg, kwargs):
        return "[correlation_id=%s] %s" % (self._correlation_id, msg), kwargs


class CorrelationLoggerMixin(object):
    """Adds ability to write correlation id to log

    Basic class must provider self.correlation_id property that
    contains current correlation identifier.

    Mixin overloads `get_logger` method that returns
    CorrelationLoggerAdapter. `get_logger` method is it special
    method that used by retries module.
    """

    def get_logger(self):
        adapter = CorrelationLoggerAdapter(self._logger, self.correlation_id)
        return adapter
