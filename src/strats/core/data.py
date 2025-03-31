class Data:
    def __init__(
        self,
        *,
        source_class=None,
        data_class=None,
        metrics_class=None,
        source_to_data=None,
        data_to_metrics=None,
        pre_init=None,
        post_init=None,
        pre_data_set=None,
        post_data_set=None,
        pre_metrics_set=None,
        post_metrics_set=None,
        pre_del=None,
        post_del=None,
        enqueue=True,
    ):
        if pre_init is not None:
            pre_init()

        # Classes
        self.source_class = source_class
        self.data_class = data_class
        self.metrics_class = metrics_class

        # ETL
        self.source_to_data = source_to_data
        self.data_to_metrics = data_to_metrics

        # Event lifecycle hook
        self.pre_init = pre_init
        self.post_init = post_init
        self.pre_data_set = pre_data_set
        self.post_data_set = post_data_set
        self.pre_metrics_set = pre_metrics_set
        self.post_metrics_set = post_metrics_set
        self.pre_del = pre_del
        self.post_del = post_del

        # Queue settings
        self.enqueue = enqueue

        # Descriptor instance name
        self._data_name = None

    def __set_name__(self, owner, name):
        self._data_name = name

        # Initialize the actual instances inside the descriptor
        self._data = self.data_class()
        self._metrics = self.metrics_class(name)

        if self.post_init is not None:
            self.post_init()

    def __get__(self, instance, owner=None):
        # When accessed as a class attribute
        if instance is None:
            return self
        return self._data

    def __set__(self, instance, new_source):
        if self.pre_data_set is not None:
            self.pre_data_set(instance, new_source)

        # Source -> Data
        if self.source_to_data is not None:
            new_data = self.source_to_data(new_source)
        else:
            new_data = new_source

        # Update Data
        self._data = new_data

        if self.enqueue:
            instance._sync_queue.put([new_source, new_data])

        if self.post_data_set is not None:
            self.post_data_set(instance, new_data)

        # Update Metrics if needed
        if self.data_to_metrics is not None:
            if self.pre_metrics_set is not None:
                self.pre_metrics_set(instance, new_data)

            # Data -> Metrics
            self.data_to_metrics(new_data, self._metrics)

            if self.post_metrics_set is not None:
                self.post_metrics_set(instance)

    def __delete__(self, instance):
        if self.pre_del is not None:
            self.pre_del(instance)

        # Reset data and metrics
        self._data = self.data_class()
        self._metrics = self.metrics_class()

        if self.enqueue:
            instance._sync_queue.put([0, 0])  # TODO

        if self.post_del is not None:
            self.post_del(instance)
