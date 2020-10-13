# -*- coding: utf-8 -*-
#
# Copyright 2017 Ricequant, Inc
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
#
#
# def load_mod():
from .mod import TushareMod


__config__ = {
    "token": "",
    "max_works": 5
}

tokens = [
    "456b1cb6d086872e59ffd4432c0ef6bc31fa1e6450a3d8b89a1d667d",
    "ddd6e0c87f1135241e6d946a0efbf9d78d0e5811cbfc78134bfa4c96",
    "0e3b219dbfbbe497afe0650997c189bbc211afa4a2a38f37023483de",
    "32bcbe7714fe65894202c39c6fa166b93d4c1d310d1e46da7f4a5a8e",
    "8438434b5690c99aae1dd2a1d8367e6606f4c98c105f9c4aa693d846",
    "f96b1eeee9c8fddd357f2299cdedc1c88b2bb2a30ae1f772cf810dea",
    "aa61aad2313a0d027f0369e3faffc0ea30cd8b1f7949c399ca502866",
    "35df2181b8de73f89857c4f48329a72a17e47f92ee520a534b0954a2",
    "68729e7d0468c4ee8fe073c11ba748700ef1812f8e2dfe34117535d9"
]

def load_mod():
    return TushareMod()
