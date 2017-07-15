define([
    'openmct',
    './src/ExampleTelemetryServerAdapter',
    './src/ExampleTelemetryInitializer',
    './src/ExampleTelemetryModelProvider'
], function (
    openmct,
    ExampleTelemetryServerAdapter,
    ExampleTelemetryInitializer,
    ExampleTelemetryModelProvider
) {
    openmct.legacyRegistry.register("tutorials/telemetry", {
        "name": "Example Telemetry Adapter",
        "extensions": {
            "types": [
                {
                    "name": "Spacecraft",
                    "key": "example.spacecraft",
                    "cssClass": "icon-object"
                },
                {
                    "name": "Subsystem",
                    "key": "example.subsystem",
                    "cssClass": "icon-object",
                    "model": { "composition": [] }
                },
                {
                    "name": "Measurement",
                    "key": "example.measurement",
                    "cssClass": "icon-telemetry",
                    "model": { "telemetry": {} },
                    "telemetry": {
                        "source": "example.source",
                        "domains": [
                            {
                                "name": "Time",
                                "key": "timestamp"
                            }
                        ]
                    }
                }
            ],
            "roots": [
                {
                    "id": "example:sc",
                    "priority": "preferred"
                }
            ],
            "models": [
                {
                    "id": "example:sc",
                    "model": {
                        "type": "example.spacecraft",
                        "name": "My Spacecraft",
                        "location": "ROOT",
                        "composition": []
                    }
                }
            ],
            "services": [
                {
                    "key": "example.adapter",
                    "implementation": "ExampleTelemetryServerAdapter.js",
                    "depends": [ "$q", "EXAMPLE_WS_URL" ]
                }
            ],
            "constants": [
                {
                    "key": "EXAMPLE_WS_URL",
                    "priority": "fallback",
                    "value": "ws://localhost:2009"
                }
            ],
            "runs": [
                {
                    "implementation": "ExampleTelemetryInitializer.js",
                    "depends": ["example.adapter", "objectService" ]
                }
            ],
            "components": [
                {
                    "provides": "modelService",
                    "type": "provider",
                    "implementation": "ExampleTelemetryModelProvider.js",
                    "depends": [ "example.adapter", "$q" ]
                },
                {
                    "provides": "telemetryService",
                    "type": "provider",
                    "implementation": "ExampleTelemetryProvider.js",
                    "depends": [ "example.adapter", "$q" ]
                }
            ]
        }
    });
});
