class InstanceManagement:
    def __init__(self, instances: list):
        self.instances = instances

    def set_empty_instances(self):
        self.instances = []

    def set_instance(self, instance):
        self.instances.append(instance)

    def get_instances(self):
        return self.instances
