import unittest
from vmaf.config import VmafConfig, VmafExternalConfig
from vmaf.core.asset import Asset
from vmaf.core.quality_runner import StrredQualityRunner, PsnrQualityRunner, \
    VmafQualityRunner, VmafossExecQualityRunner
from vmaf.core.result_store import FileSystemResultStore

__copyright__ = "Copyright 2016-2017, Netflix, Inc."
__license__ = "Apache, Version 2.0"


@unittest.skipIf(not VmafExternalConfig.ffmpeg_path(), "ffmpeg not installed")
class QualityRunnerTest(unittest.TestCase):

    def tearDown(self):
        if hasattr(self, 'runner'):
            self.runner.remove_results()
            pass

    def setUp(self):
        self.result_store = FileSystemResultStore()

    def test_run_psnr_runner_with_notyuv(self):
        print 'test on running PSNR runner...'
        ref_path = VmafConfig.test_resource_path("mp4", "Seeking_10_288_375.mp4")
        dis_path = VmafConfig.test_resource_path("mp4", "Seeking_10_288_375.mp4")
        asset = Asset(dataset="test", content_id=0, asset_id=0,
                      workdir_root=VmafConfig.workdir_path(),
                      ref_path=ref_path,
                      dis_path=dis_path,
                      asset_dict={'yuv_type': 'notyuv',
                                  'quality_width': 720, 'quality_height': 480,
                                  })
        self.runner = PsnrQualityRunner(
            [asset],
            None, fifo_mode=True,
            delete_workdir=True,
            result_store=None
        )
        self.runner.run()

        results = self.runner.results
        self.assertAlmostEqual(results[0]['PSNR_score'], 60.0, places=4)

    def test_run_vmaf_runner_with_notyuv(self):
        print 'test on running VMAF runner...'
        ref_path = VmafConfig.test_resource_path("mp4", "Seeking_30_480_1050.mp4")
        dis_path = VmafConfig.test_resource_path("mp4", "Seeking_10_288_375.mp4")
        asset = Asset(dataset="test", content_id=0, asset_id=0,
                      workdir_root=VmafConfig.workdir_path(),
                      ref_path=ref_path,
                      dis_path=dis_path,
                      asset_dict={'yuv_type': 'notyuv',
                                  'quality_width': 360, 'quality_height': 240,
                                  })
        self.runner = VmafQualityRunner(
            [asset],
            None, fifo_mode=True,
            delete_workdir=True,
            result_store=None
        )
        self.runner.run()

        results = self.runner.results
        self.assertAlmostEqual(results[0]['VMAF_score'], 79.052553444706504, places=4)

    def test_run_vmafossexec_runner_with_notyuv(self):
        print 'test on running VMAF runner...'
        ref_path = VmafConfig.test_resource_path("mp4", "Seeking_30_480_1050.mp4")
        dis_path = VmafConfig.test_resource_path("mp4", "Seeking_10_288_375.mp4")
        asset = Asset(dataset="test", content_id=0, asset_id=0,
                      workdir_root=VmafConfig.workdir_path(),
                      ref_path=ref_path,
                      dis_path=dis_path,
                      asset_dict={'yuv_type': 'notyuv',
                                  'quality_width': 360, 'quality_height': 240,
                                  })
        self.runner = VmafossExecQualityRunner(
            [asset],
            None, fifo_mode=True,
            delete_workdir=True,
            result_store=None
        )
        self.runner.run()

        results = self.runner.results
        self.assertAlmostEqual(results[0]['VMAFOSSEXEC_score'], 79.052553444706504, places=4)


@unittest.skipIf(not VmafExternalConfig.matlab_path(), "matlab not installed")
class ParallelQualityRunnerTest(unittest.TestCase):

    def tearDown(self):
        if hasattr(self, 'runner'):
            self.runner.remove_results()
            pass

    def setUp(self):
        self.result_store = FileSystemResultStore()

    def test_run_strrred_runner(self):
        print 'test on running STRRED runner...'
        ref_path = VmafConfig.test_resource_path("yuv", "src01_hrc00_576x324.yuv")
        dis_path = VmafConfig.test_resource_path("yuv", "src01_hrc01_576x324.yuv")
        asset = Asset(dataset="test", content_id=0, asset_id=0,
                      workdir_root=VmafConfig.workdir_path(),
                      ref_path=ref_path,
                      dis_path=dis_path,
                      asset_dict={'width':576, 'height':324})

        asset_original = Asset(dataset="test", content_id=0, asset_id=1,
                      workdir_root=VmafConfig.workdir_path(),
                      ref_path=ref_path,
                      dis_path=ref_path,
                      asset_dict={'width':576, 'height':324})

        self.runner = StrredQualityRunner(
            [asset, asset_original],
            None, fifo_mode=True,
            delete_workdir=True,
            result_store=None
        )
        self.runner.run(parallelize=True)

        results = self.runner.results

        self.assertAlmostEqual(results[0]['STRRED_feature_srred_score'], 3.0115371666666668, places=4)
        self.assertAlmostEqual(results[0]['STRRED_feature_trred_score'], 7.2454298124999994, places=4)
        self.assertAlmostEqual(results[0]['STRRED_score'], 21.905674926201982, places=4)
        self.assertAlmostEqual(results[1]['STRRED_feature_srred_score'], 0.0, places=4)
        self.assertAlmostEqual(results[1]['STRRED_feature_trred_score'], 0.0, places=4)
        self.assertAlmostEqual(results[1]['STRRED_score'], 0.0, places=4)


if __name__ == '__main__':
    unittest.main()