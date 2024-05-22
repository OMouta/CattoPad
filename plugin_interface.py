from abc import ABC, abstractmethod

class PluginInterface(ABC):
    @abstractmethod
    async def run(self, main_window):
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_version(self):
        pass

    @abstractmethod
    def get_author(self):
        pass

    @abstractmethod
    def get_description(self):
        pass
    
    @abstractmethod
    def run_on_startup(self):
        pass

    @abstractmethod
    def needs_runtime(self):
        pass