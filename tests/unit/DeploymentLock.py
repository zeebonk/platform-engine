# -*- coding: utf-8 -*-
from asyncy.DeploymentLock import DeploymentLock

from pytest import mark


@mark.asyncio
async def test_locking():
    lock = DeploymentLock()
    assert await lock.try_acquire('my_app_1') is True
    assert await lock.try_acquire('my_app_1') is False
    assert await lock.try_acquire('my_app_1') is False
    assert await lock.try_acquire('my_app_2') is True
    assert await lock.try_acquire('my_app_2') is False
    assert await lock.try_acquire('my_app_1') is False
    await lock.release('my_app_1')
    assert await lock.try_acquire('my_app_1') is True
    assert await lock.try_acquire('my_app_2') is False
    await lock.release('my_app_2')
    assert await lock.try_acquire('my_app_2') is True
