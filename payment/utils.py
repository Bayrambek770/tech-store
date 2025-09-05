class PaylovMethods:
    CHECK_TRANSACTION = "transaction.check"
    PERFORM_TRANSACTION = "transaction.perform"

    @classmethod
    def choices(cls):
        return (
            (cls.CHECK_TRANSACTION, cls.CHECK_TRANSACTION),
            (cls.PERFORM_TRANSACTION, cls.PERFORM_TRANSACTION),
        )
