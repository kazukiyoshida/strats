import functools

from fastapi import FastAPI

from strats.core.kernel import Kernel
from strats.core.lifecycle import get_lifecycle_handlers

from .middleware import AccessLogMiddleware
from .router import get_kernel, router

BANNER = r"""
 _______ _______  ______ _______ _______ _______
 |______    |    |_____/ |_____|    |    |______
 ______|    |    |     \ |     |    |    ______|
"""


def kernel_getter_factory(kernel):
    def kernel_getter():
        return kernel

    return kernel_getter


class Strats(Kernel):
    def create_app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_kernel] = kernel_getter_factory(self)

        if self.config.install_access_log:
            app.add_middleware(
                AccessLogMiddleware,
                drop_paths=self.config.drop_access_log_paths,
            )

        # Register all globally collected lifecycle hooks
        for fn in get_lifecycle_handlers("startup"):
            # Pass kernel iteself to the lifecycle function
            fn_ = functools.partial(fn, self)
            app.add_event_handler("startup", fn_)
        for fn in get_lifecycle_handlers("shutdown"):
            # Pass kernel iteself to the lifecycle function
            fn_ = functools.partial(fn, self)
            app.add_event_handler("shutdown", fn_)

        return app
