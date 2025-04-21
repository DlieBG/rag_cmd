from src.models.sample import SampleCommand, SampleCommandCreate, SampleCommandId

class SampleProvider:
    def get_samples(self) -> list[SampleCommand]:
        raise NotImplementedError()

    def get_sample(self, id: str) -> SampleCommand:
        raise NotImplementedError()
    
    def create_sample(self, sample: SampleCommandCreate) -> SampleCommandId:
        raise NotImplementedError()
    
    def update_sample(self, id: str, sample: SampleCommand):
        raise NotImplementedError()
    
    def remove_sample(self, id: str):
        raise NotImplementedError()
