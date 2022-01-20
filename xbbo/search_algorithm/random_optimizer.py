from xbbo.core.trials import Trial, Trials
from xbbo.initial_design import ALL_avaliable_design
from xbbo.search_algorithm.base import AbstractOptimizer
from . import alg_register

@alg_register.register('rs')
class RandomOptimizer(AbstractOptimizer):
    def __init__(
            self,
            space,
            seed: int = 42,
            initial_design: str = 'sobol',
            #  min_sample=1,
            total_limit: int = 10,
            **kwargs):
        AbstractOptimizer.__init__(self,
                                   space,
                                   encoding_cat='round',
                                   encoding_ord='round',
                                   seed=seed,
                                   **kwargs)
        self.initial_design = ALL_avaliable_design[initial_design](
            self.space, self.rng, ta_run_limit=total_limit,**kwargs)
        self.init_budget = self.initial_design.init_budget
        self.initial_design_configs = self.initial_design.select_configurations(
        )
        self.dimension = self.space.get_dimensions()
        self.trials = Trials(dim=self.dimension)


    def suggest(self, n_suggestions=1):
        trial_list = []
        for n in range(n_suggestions):
            if self.initial_design_configs:
                config = self.initial_design_configs.pop(0)
                trial_list.append(
                    Trial(
                        configuration=config,
                          config_dict=config.get_dictionary(),
                        #   array=config.get_array())
                    ))
                continue
            iter_ = 0
            while iter_ < 1000:  # remove history suggest
                config = self.space.sample_configuration()[0]
                if not self.trials.is_contain(config):
                    trial_list.append(
                        Trial(configuration=config,
                              config_dict=config.get_dictionary(),
                              array=config.get_array()))

                    break
                iter_ += 1
            else:
                assert False, "no more configs can be suggest"

        return trial_list

    def observe(self, trial_list):
        for trial in trial_list:
            self.trials.add_a_trial(trial)


opt_class = RandomOptimizer