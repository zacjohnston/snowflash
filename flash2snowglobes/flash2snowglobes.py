# FLASH to snowglobes wrapper code
# Need working installation of snowglobes
# This will convert FLASH data to necessary input format for snowglobes,
# run snowglobes, analyze the output, and clean up files

import read_flash

import cleanup
import config
import convert
import write_files
import analysis
import run_snowglobes
import setup
import flavor_mixing


print('=== Copying snowglobes install ===')
setup.copy_snowglobes(config.snowglobes_path)

for mixing in config.mixing:
    for model_set in config.model_sets:
        for mass in config.masses:
            print('=== Converting flash data ===')
            time, lum, avg, rms = read_flash.read_datfile(model_set=model_set,
                                                          mass=mass,
                                                          t_start=config.t_start,
                                                          t_end=config.t_end)

            fluences = convert.get_fluences(time=time,
                                            lum=lum,
                                            avg=avg,
                                            rms=rms,
                                            distance=config.distance,
                                            timebins=config.timebins,
                                            e_bins=config.e_bins)

            fluences_mixed = flavor_mixing.mix_fluences(fluences=fluences,
                                                        mixing=mixing)

            write_files.write_fluence_files(model_set=model_set,
                                            mass=mass,
                                            timebins=config.timebins,
                                            e_bins=config.e_bins,
                                            fluences_mixed=fluences_mixed)

            print('=== Running snowglobes ===')
            run_snowglobes.run(model_set=model_set,
                               mass=mass,
                               timebins=config.timebins,
                               material=config.material,
                               detector=config.detector)

            print('=== Analyzing output ===')
            analysis.analyze_output(model_set=model_set,
                                    mass=mass,
                                    detector=config.detector,
                                    channel_groups=config.channel_groups,
                                    mixing=mixing)

            print('=== Cleaning up model ===')
            cleanup.clean_model()

print('=== Final cleanup ===')
cleanup.clean_all()
