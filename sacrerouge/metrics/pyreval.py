import argparse
import logging
import os
import shutil
from glob import glob
from overrides import overrides
from subprocess import Popen, PIPE
from typing import Dict, List, Tuple

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.data import MetricsDict
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric

logger = logging.getLogger(__name__)


@Metric.register('pyreval')
class PyrEval(ReferenceBasedMetric):
    def __init__(self,
                 environment_name: str = None,
                 pyreval_root: str = f'{DATA_ROOT}/metrics/PyrEval',
                 verbose: bool = False):
        super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())
        self.environment_name = environment_name
        self.pyreval_root = pyreval_root
        self.verbose = verbose

        if self.environment_name is not None:
            if 'CONDA_INIT' not in os.environ:
                raise Exception('If `environment_name` is not none, environment variable "CONDA_INIT" must be set to the path to "conda.sh"')

    def _clean_directories(self):
        # The PyrEval code runs all of its processing in place, so we need to clean up all of its
        # directories in case there is something left over from an old run, which might cause a problem
        # for the next run.
        #
        # This code is based on the clean function in "pyreval.py". The original code will crash if one of
        # the directories it searches for does not exist, so we reimplemented it here.

        # Clean the raw data (not included in the original code)
        for file_path in glob(f'{self.pyreval_root}/Raw/peers/*'):
            if os.path.isfile(file_path):
                os.remove(file_path)
        for file_path in glob(f'{self.pyreval_root}/Raw/model/*'):
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Clean the sentence splits
        for file_path in glob(f'{self.pyreval_root}/Raw/peers/split/*'):
            os.remove(file_path)
        for file_path in glob(f'{self.pyreval_root}/Raw/model/split/*'):
            os.remove(file_path)

        # Clean the preprocessed folder, first the files, then the folders
        for file_path in glob(f'{self.pyreval_root}/Preprocess/peer_summaries/*.xml'):
            os.remove(file_path)
        for dir_path in glob(f'{self.pyreval_root}/Preprocess/peer_summaries/*'):
            shutil.rmtree(dir_path)

        for file_path in glob(f'{self.pyreval_root}/Preprocess/wise_crowd_summaries/*.xml'):
            os.remove(file_path)
        for dir_path in glob(f'{self.pyreval_root}/Preprocess/wise_crowd_summaries/*'):
            shutil.rmtree(dir_path)

        # Pyramid scores
        scores_file = f'{self.pyreval_root}/Pyramid/scores.txt'
        if os.path.exists(scores_file):
            os.remove(scores_file)

        # Pyramids
        for file_path in glob(f'{self.pyreval_root}/Scoring/pyrs/pyramids/*.pyr'):
            os.remove(file_path)

        # SCUs
        for file_path in glob(f'{self.pyreval_root}/Scoring/scu/*.pyr'):
            os.remove(file_path)

        # Sizes
        for file_path in glob(f'{self.pyreval_root}/Scoring/sizes/*.size'):
            os.remove(file_path)

        # Temp
        for file_path in glob(f'{self.pyreval_root}/Scoring/temp/*'):
            os.remove(file_path)

        # The results file
        results_file = f'{self.pyreval_root}/results.csv'
        if os.path.exists(results_file):
            os.remove(results_file)

    def _flatten_summaries(self, summaries_list: List[List[SummaryType]]) -> List[List[str]]:
        flat_list = []
        for summaries in summaries_list:
            flat_list.append([])
            for summary in summaries:
                if isinstance(summary, list):
                    summary = ' '.join(summary)
                flat_list[-1].append(summary)
        return flat_list

    def _index_summaries(self,
                         summaries_list: List[List[str]],
                         references_list: List[List[str]]) -> Tuple[List[str], Dict[str, int]]:
        index_to_summary = []
        summary_to_index = {}
        for summs_list in [summaries_list, references_list]:
            for summaries in summs_list:
                for summary in summaries:
                    if summary not in summary_to_index:
                        index_to_summary.append(summary)
                        summary_to_index[summary] = len(summary_to_index)
        return index_to_summary, summary_to_index

    def _save_summaries(self, summaries: List[str], output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        for i, summary in enumerate(summaries):
            with open(f'{output_dir}/{i}', 'w') as out:
                out.write(summary)

    def _run_through_preprocessing(self) -> None:
        logging.info('Running PyrEval through preprocessing')

        # Each of the steps must be done manually, otherwise the "pyreval.py" code would try to run the preprocessing
        # on both the peer and the model directories. We only want it to do the peer directory.
        #
        # Sentence splitting
        commands = [f'cd {self.pyreval_root}']
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'python2.7 split-sent.py {self.pyreval_root}/Raw/peers {self.pyreval_root}/Raw/peers/split')
        command = ' && '.join(commands)

        logger.info(f'Running command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

        # Stanford
        commands = [f'cd {self.pyreval_root}/Stanford']
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'python2.7 stanford.py {self.pyreval_root}/Raw/peers/split 1 ..')
        command = ' && '.join(commands)

        logger.info(f'Running command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

        # Preprocess
        commands = [f'cd {self.pyreval_root}/Preprocess']
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'python2.7 preprocess.py 1')
        command = ' && '.join(commands)

        logger.info(f'Running command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

        logging.info('Finished preprocessing')

    def _map_file_index_to_directory(self, input_dir: str) -> Dict[int, int]:
        # Each directory has a file "x.ls" where "x" is the summary index
        mapping = {}
        for path in glob(f'{input_dir}/*/*.ls'):
            filename = os.path.basename(path)
            file_index = int(os.path.splitext(filename)[0])
            dir_index = int(os.path.basename(os.path.dirname(path)))
            mapping[file_index] = dir_index
        return mapping

    def _move_summaries_to_temp_dir(self, temp_dir: str):
        os.makedirs(f'{temp_dir}/peers', exist_ok=True)
        for path in glob(f'{self.pyreval_root}/Preprocess/peer_summaries/*'):
            shutil.move(path, f'{temp_dir}/peers/')

    def _copy_file_and_change_id(self, src: str, tgt: str, new_id: int):
        # The processing will fail if the document id isn't aligned with the directory the file is in. The document id
        # is the first entry in each line of these files, where each column is separated with &
        with open(tgt, 'w') as out:
            with open(src, 'r') as f:
                for line in f:
                    columns = line.strip().split('&')
                    columns[0] = str(new_id)
                    out.write('&'.join(columns) + '\n')

    def _copy_summaries_for_processing(self,
                                       summaries: List[str],
                                       summary_to_index: Dict[str, int],
                                       file_index_to_dir_index: Dict[int, int],
                                       input_dir: str,
                                       output_dir: str,
                                       sort_summaries: bool) -> None:
        os.makedirs(output_dir, exist_ok=True)

        # The PyrEval code changes its output based on the order of the references, so we sort if necessary
        # to keep the results deterministic
        if sort_summaries:
            summaries = sorted(summaries)

        # Copy the summaries from the temporary directory over to the PyrEval directory. The target directories
        # must be 1, 2, ...
        for i, summary in enumerate(summaries):
            file_index = summary_to_index[summary]
            src = f'{input_dir}/{file_index}.xml'
            tgt = f'{output_dir}/{i}.xml'
            logging.info(f'Copying {src} to {tgt}')
            shutil.copy(f'{src}', f'{tgt}')

            dir_index = file_index_to_dir_index[file_index]
            src_dir = f'{input_dir}/{dir_index}'
            tgt_dir = f'{output_dir}/{i + 1}'
            os.makedirs(tgt_dir)
            for ext in ['.ls', '.segs']:
                src = f'{src_dir}/{file_index}{ext}'
                tgt = f'{tgt_dir}/{i}{ext}'
                logging.info(f'Copying {src} to {tgt}, updating document ID to {i + 1}')
                self._copy_file_and_change_id(src, tgt, i + 1)

    def _score_summaries(self) -> List[MetricsDict]:
        logging.info('Building pyramids and scoring peers')

        # Each step can be run by piping its ID into the pyreval.py program.
        #   4: pyramid
        #   5 -t: score (-t means to write the results to file)
        for args in ['4', '5 -t']:
            commands = [f'cd {self.pyreval_root}']
            if self.environment_name is not None:
                commands.append(f'source {os.environ["CONDA_INIT"]}')
                commands.append(f'conda activate {self.environment_name}')
            commands.append(f'echo {args} | python2.7 pyreval.py')
            command = ' && '.join(commands)

            logger.info(f'Running command: "{command}"')
            redirect = None if self.verbose else PIPE
            process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
            process.communicate()

        # Parse the results
        results_path = f'{self.pyreval_root}/results.csv'
        if not os.path.exists(results_path):
            raise Exception(f'PyrEval results file does not exist: "{results_path}"')

        # First line is the name of the pyramid
        # Second line is the header
        lines = open(results_path, 'r').read().splitlines()
        metrics_dicts = {}
        for line in lines[2:]:
            index, raw, quality, coverage, comprehensive = line.split(',')
            metrics_dicts[int(index)] = MetricsDict({
                'pyreval': {
                    'raw': int(raw),
                    'quality': float(quality),
                    'coverage': float(coverage),
                    'comprehensive': float(comprehensive),
                }
            })

        metrics_list = []
        for index in range(len(metrics_dicts)):
            metrics_list.append(metrics_dicts[index])

        logging.info('Finished building pyramids and scoring peers')
        return metrics_list

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        # The original code for PyrEval processes exactly 1 pyramid at a time. Therefore, the whole pipeline needs
        # to be run once per item in `references_list`. Each execution of the pipeline will load the Stanford CoreNLP
        # models and run them over the text. Loading the models takes a lot of time, and the preprocessing of
        # the same summary may run multiple times (for instance in jackknifing).
        #
        # To save time, our implementation passes all of the unique peer and reference summaries through the
        # preprocessing step of the pipeline at once, then runs the analysis step per-pyramid afterward. This
        # significantly increases the speed of the processing.

        # Identify the unique summaries so less preprocessing needs to be done
        summaries_list = self._flatten_summaries(summaries_list)
        references_list = self._flatten_summaries(references_list)

        all_summaries, summary_to_index = self._index_summaries(summaries_list, references_list)

        with TemporaryDirectory() as temp_dir:
            # First, clear the PyrEval directory in case the last run was messed up
            self._clean_directories()

            # All of the summaries are saved in the "peers" folder, even if they are references. The PyrEval code
            # normally runs separate steps to process the peer and model directories, which is slower because it requires
            # loading the Stanford models twice, but the preprocessing is the same.
            self._save_summaries(all_summaries, f'{self.pyreval_root}/Raw/peers')

            self._run_through_preprocessing()

            # The PyrEval code will create an xml for summary i called i.xml and a directory with more data for
            # that file. The directory names aren't consistent because they're created by enumerating glob results
            # (which I think are not always deterministically sorted, or I don't want to rely on the assumption
            # that they are sorted). So we have to figure out the mapping from the summary index to the directory
            file_index_to_dir = self._map_file_index_to_directory(f'{self.pyreval_root}/Preprocess/peer_summaries')

            # All of the preprocessed summaries are now moved out of the PyrEval directory (or else they would be
            # used in the rest of the processing) to a temporary directory
            self._move_summaries_to_temp_dir(temp_dir)

            # Remove any extra data which could interfere with processing
            self._clean_directories()

            # Now build the pyramids and score
            metrics_dict_lists = []
            for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
                self._copy_summaries_for_processing(summaries,
                                                    summary_to_index,
                                                    file_index_to_dir,
                                                    f'{temp_dir}/peers',
                                                    f'{self.pyreval_root}/Preprocess/peer_summaries',
                                                    False)
                self._copy_summaries_for_processing(references,
                                                    summary_to_index,
                                                    file_index_to_dir,
                                                    f'{temp_dir}/peers',
                                                    f'{self.pyreval_root}/Preprocess/wise_crowd_summaries',
                                                    True)

                metrics_list = self._score_summaries()
                metrics_dict_lists.append(metrics_list)

                # Clean for the next iteration
                self._clean_directories()

            return metrics_dict_lists


class PyrEvalSetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the PyrEval metric'
        self.parser = parser.add_parser('pyreval', description=description, help=description)
        self.parser.add_argument('--force', action='store_true', help='Force setting up the metric again')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        if args.force and os.path.exists(f'{DATA_ROOT}/metrics/PyrEval'):
            shutil.rmtree(f'{DATA_ROOT}/metrics/PyrEval')

        commands = [
            f'mkdir -p {DATA_ROOT}/metrics',
            f'cd {DATA_ROOT}/metrics',
            f'git clone https://github.com/danieldeutsch/PyrEval',
            f'cd PyrEval',
            f'wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip',
            f'unzip stanford-corenlp-full-2018-10-05.zip',
            f'mv stanford-corenlp-full-2018-10-05/* Stanford/',
            f'rm stanford-corenlp-full-2018-10-05.zip'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()

        if process.returncode == 0:
            print('PyrEval setup success')
        else:
            print('PyrEval setup failure')
