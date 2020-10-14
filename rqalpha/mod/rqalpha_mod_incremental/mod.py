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

import os
import datetime

from rqalpha.utils.logger import system_log
from rqalpha.interface import AbstractMod
from rqalpha.events import EVENT
from rqalpha.const import PERSIST_MODE
from rqalpha.utils.disk_persist_provider import DiskPersistProvider
from rqalpha.utils.i18n import gettext as _

from . import persist_providers, recorders
from .incremental_event_source import IncrementalEventSource
from .base_data_source.data_source import IncrementcalDataSource


class IncrementalMod(AbstractMod):
    def __init__(self):
        self._env = None
        self._start_date = None
        self._end_date = None

    def start_up(self, env, mod_config):
        self._env = env
        self._recorder = None
        self._mod_config = mod_config

        self._set_env_and_data_source()

        env.config.base.persist = True
        env.config.base.persist_mode = PERSIST_MODE.ON_NORMAL_EXIT

        env.event_bus.add_listener(EVENT.POST_SYSTEM_INIT, self._init)

    def _set_env_and_data_source(self):
        env = self._env
        mod_config = self._mod_config
        system_log.info("use recorder {}", mod_config.recorder)
        if mod_config.recorder == "CsvRecorder":
            if not mod_config.persist_folder:
                raise RuntimeError(_(u"You need to set persist_folder to use CsvRecorder"))
            persist_provider = DiskPersistProvider(os.path.join(mod_config.persist_folder, "persist"))
            self._recorder = recorders.CsvRecorder(mod_config.persist_folder)
        elif mod_config.recorder == "MongodbRecorder":
            if mod_config.strategy_id is None:
                raise RuntimeError(_(u"You need to set strategy_id"))
            persist_provider = persist_providers.MongodbPersistProvider(mod_config.strategy_id, mod_config.mongo_url,
                                                                        mod_config.mongo_dbname)
            self._recorder = recorders.MongodbRecorder(mod_config.strategy_id,
                                                       mod_config.mongo_url, mod_config.mongo_dbname)
        else:
            raise RuntimeError(_(u"unknown recorder {}").format(mod_config.recorder))

        if env.persist_provider is None:
            env.set_persist_provider(persist_provider)

        self._meta = {
            "strategy_id": mod_config.strategy_id,
            "origin_start_date": self._env.config.base.start_date.strftime("%Y-%m-%d"),
            "start_date": self._env.config.base.start_date.strftime("%Y-%m-%d"),
            "end_date": self._env.config.base.end_date.strftime("%Y-%m-%d"),
            "last_end_time": self._env.config.base.end_date.strftime("%Y-%m-%d"),
            "last_run_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        event_start_time = self._env.config.base.start_date
        persist_meta = self._recorder.load_meta()
        if persist_meta:
            # 不修改回测开始时间
            self._env.config.base.start_date = persist_meta['start_date']
            event_start_time = datetime.datetime.strptime(persist_meta['last_end_time'], '%Y-%m-%d').date() + datetime.timedelta(days=1)
            # 代表历史有运行过，根据历史上次运行的end_date下一天设为事件发送的start_time

            self._meta["origin_start_date"] = persist_meta["origin_start_date"]
            self._meta["start_date"] = persist_meta["start_date"]
            self._meta["last_end_time"] = self._env.config.base.end_date.strftime("%Y-%m-%d")
        env.set_data_source(IncrementcalDataSource(self._env.config.base.data_bundle_path,
                                                   getattr(self._env.config.base, "future_info", {}),
                                                   self._env.config.base.start_date))

        event_source = IncrementalEventSource(env, event_start_time, self._env.config.base.end_date)
        env.set_event_source(event_source)

    def _init(self, event):
        env = self._env
        env.event_bus.add_listener(EVENT.TRADE, self.on_trade)
        env.event_bus.add_listener(EVENT.POST_SETTLEMENT, self.on_settlement)

    def on_trade(self, event):
        pass

    def on_settlement(self, event):
        pass

    def tear_down(self, success, exception=None):
        if exception is None:
            self._recorder.store_meta(self._meta)
            self._recorder.flush()
            self._recorder.close()
