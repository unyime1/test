import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import services.tasks as tasks
from routers.register import router as register_router
from routers.auth import router as auth_router
from library.utils.parameters import get_ssm_parameters


def get_application():
    # start the application
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_event_handler("startup", tasks.create_start_app_handler(app))
    app.include_router(register_router)
    app.include_router(auth_router)

    parameters = get_ssm_parameters()

    sentry_sdk.init(
        dsn=parameters["sentry_accounts"],
        traces_sample_rate=1.0,
    )

    return app


app = get_application()


@app.get("/", name="root")
async def home():
    return {"status": "Hello world"}
