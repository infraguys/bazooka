#    Copyright 2025 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from urllib import parse
from typing import Optional, Iterable


def force_last_slash(path: str) -> str:
    """
    Force path to have a trailing slash.

    :param path: The path to be adjusted
    :return: The path with a trailing slash
    """
    return path if path.endswith("/") else f"{path}/"


class RESTClientMixIn:
    """Mixin class providing REST URI construction utilities."""

    def _build_resource_uri(
        self, paths: Iterable[str], init_uri: Optional[str] = None
    ) -> str:
        """
        Construct a full URI from a list of path components and an optional
        initial URI.

        :param paths: An iterable of path components
        :param init_uri: An optional initial URI
        :return: A full URI constructed from the components
        :raises AttributeError: If no initial URI is provided and the object
            lacks an '_endpoint' attribute.
        """
        uri = (
            init_uri
            if init_uri is not None
            else getattr(self, "_endpoint", None)
        )
        if uri is None:
            raise AttributeError(
                "No initial URI provided and '_endpoint'"
                " attribute is not set."
            )

        for path in paths:
            uri = parse.urljoin(force_last_slash(uri), str(path).lstrip("/"))

        return uri

    def _build_collection_uri(
        self, paths: Iterable[str], init_uri: Optional[str] = None
    ) -> str:
        """
        Construct a full URI from a list of path components, as if the
        resulting URI is a collection resource.

        :param paths: An iterable of path components
        :param init_uri: An optional initial URI (default is None)
        :return: A full URI constructed from the components
        """
        return force_last_slash(self._build_resource_uri(paths, init_uri))
