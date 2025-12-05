class SetupReaderFormDefaults:
    """
    Legacy default values for setup forms.

    DEPRECATED: This class is maintained for backward compatibility only.
    New code should use SetupFormConfig with use-case-specific defaults.

    These defaults are only used when SetupReaderFormInput is created
    without a config parameter.
    """
    def __init__(self):
        self.scanRate = "5"
        self.calibrate = True
        self.equilibrationTime = "24"


