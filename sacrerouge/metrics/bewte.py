import argparse
import logging
import os
from collections import defaultdict
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List, Tuple

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.common.util import command_exists
from sacrerouge.data import MetricsDict
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric

logger = logging.getLogger(__name__)


@Metric.register('bewte')
class BEwTE(Metric):
    def __init__(self,
                 bewte_root: str = f'{DATA_ROOT}/metrics/ROUGE-BEwTE',
                 verbose: bool = False):
        super().__init__(['references'], jackknifer=ReferencesJackknifer())
        self.bewte_root = bewte_root
        if not os.path.exists(bewte_root):
            raise Exception('BEwTE directory does not exist. Please run the setup code')
        self.pos_model = f'src/main/resources/models/posTaggingModel.gz'
        self.parsing_model = f'src/main/resources/models/parseModel.gz'
        self.wordnet_dir = f'src/main/resources/data/wordnet3_0'
        self.opennlp_dir = f'src/main/resources/models/opennlp'
        self.rule_file = f'src/main/resources/conf/rules/EN_ruleList.txt'
        self.transforms_file = f'src/main/resources/conf/transformations/EN_transformsList.txt'
        self.transforms_coef_file = f'src/main/resources/conf/transformations/EN_transformCoeffs.txt'
        self.end_analysis_file = f'src/main/resources/conf/endanalysis/doNothingEndAnalysisConfig.txt'
        self.verbose = verbose

    def _save_summary(self, summary: SummaryType, file_path: str) -> None:
        dirname = os.path.dirname(file_path)
        os.makedirs(dirname, exist_ok=True)
        with open(file_path, 'w') as out:
            if isinstance(summary, list):
                out.write('\n'.join(summary))
            else:
                out.write(summary)

    def _save_summaries(self,
                        temp_dir: str,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[SummaryType]]) -> None:
        for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
            for j, summary in enumerate(summaries):
                self._save_summary(summary, f'{temp_dir}/summaries/{i}.{j}')
            for j, reference in enumerate(references):
                symbol = chr(j + 65)
                self._save_summary(reference, f'{temp_dir}/summaries/{i}.{symbol}')

    def _run_step1(self, temp_dir: str) -> None:
        args = ' '.join([
            '-corpusreader',
            'tratz.runpipe.impl.corpusreader.DirectoryCorpusReader',
            f'InputDirectories={temp_dir}/summaries',
            '-documentreader',
            'bewte.io.StandardTextDocReader',
            '-annotator',
            'tratz.runpipe.impl.annotators.sentence.BreakIteratorSentenceAnnotator',
            'ONLY_WHEN_NECESSARY=true',
            '-annotator',
            'bewte.annotators.RegexTokenizer',
            '-annotator',
            'tratz.runpipe.impl.annotators.pos.TratzPosTaggerAnnotator',
            f'ModelFile={self.pos_model}',
            f'WordNetDir={self.wordnet_dir}',
            '-annotator',
            'tratz.runpipe.impl.annotators.parse.TratzParserAnnotator',
            f'ModelFile={self.parsing_model}',
            f'WordNetDir={self.wordnet_dir}',
            'VchTransform=true',
            '-endpoint',
            'tratz.runpipe.impl.endpoints.GzippedDocumentWriter',
            f'OutputDir={temp_dir}/eval/temp/parsed'
        ])

        commands = [
            f'cd {self.bewte_root}',
            f'mvn exec:java@RunPipe -Dexec.args=\'{args}\''
        ]
        command = ' && '.join(commands)

        logger.info(f'Running BEwTE step 1 command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

    def _run_step2(self, temp_dir: str) -> None:
        args = ' '.join([
            '-corpusreader',
            'tratz.runpipe.impl.corpusreader.GzippedCorpusReader',
            f'InputDirectories={temp_dir}/eval/temp/parsed',
            '-annotator',
            'tratz.runpipe.impl.annotators.parse.TokenFieldUpdater',
            f'WordNetDir={self.wordnet_dir}',
            '-annotator',
            'runpipewrappers.ner.OpenNlpNerWrapper',
            f'ModelPath={self.opennlp_dir}/person.bin.gz',
            'AnnotationClass=tratz.runpipe.annotations.PersonAnnotation',
            '-annotator',
            'runpipewrappers.ner.OpenNlpNerWrapper',
            f'ModelPath={self.opennlp_dir}/organization.bin.gz',
            'AnnotationClass=tratz.runpipe.annotations.OrganizationAnnotation',
            '-annotator',
            'runpipewrappers.ner.OpenNlpNerWrapper',
            f'ModelPath={self.opennlp_dir}/location.bin.gz',
            'AnnotationClass=tratz.runpipe.annotations.LocationAnnotation',
            '-endpoint',
            'bewte.beextraction.BasicElementExtractor',
            f'OutputDir={temp_dir}/eval/temp/BEs'
        ])

        commands = [
            f'cd {self.bewte_root}',
            f'mvn exec:java@RunPipe -Dexec.args=\'{args}\''
        ]
        command = ' && '.join(commands)

        logger.info(f'Running BEwTE step 2 command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

    def _run_step3(self, temp_dir: str) -> None:
        args = ' '.join([
            f'{temp_dir}/eval/temp/BEs',
            f'{temp_dir}/eval/temp/BEXs',
            self.wordnet_dir,
            '0',
            '-1',
            '.*[A-Z_\\-]+',
            self.transforms_file,
            'bewte.names.DUCStyleNameExtractor'
        ])

        commands = [
            f'cd {self.bewte_root}',
            f'mvn exec:java@BEXpander -Dexec.args=\'{args}\''
        ]
        command = ' && '.join(commands)

        logger.info(f'Running BEwTE step 3 command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

    def _run_step4(self, temp_dir: str) -> None:
        args = ' '.join([
            f'{temp_dir}/eval/temp/BEXs',
            f'{temp_dir}/systemLevelOutput.txt',
            f'{temp_dir}/summaryLevelOutput.txt',
            'bewte.scoring.TallyFunction$BinaryTallyFunction',
            'false',
            self.rule_file,
            self.transforms_file,
            self.transforms_coef_file,
            '[A-Z_\\-]+',
            self.end_analysis_file,
            'bewte.names.DUCStyleNameExtractor',
            '.*'
        ])

        commands = [
            f'cd {self.bewte_root}',
            f'mvn exec:java@BEwT_E -Dexec.args=\'{args}\''
        ]
        command = ' && '.join(commands)

        logger.info(f'Running BEwTE step 4 command: "{command}"')

        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, _ = process.communicate()
        return stdout.decode()

    def _get_topic_and_system(self, line: str) -> Tuple[int, str]:
        last_slash = line.rfind('/')
        last_period = line.rfind('.')

        topic = int(line[last_slash + 1:last_period])
        system = line[last_period + 1:]
        return topic, system

    def _get_f1(self, line: str) -> Tuple[float, float, float]:
        columns = line.split()
        precision = float(columns[3][2:]) * 100
        recall = float(columns[4][2:]) * 100
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        return precision, recall, f1

    def _parse_stdout(self, stdout: str) -> List[List[MetricsDict]]:
        lines = stdout.splitlines()
        metrics_dicts = defaultdict(lambda: defaultdict(MetricsDict))

        index = 0
        while index < len(lines):
            line = lines[index].strip()
            if line.startswith('Peer:'):
                topic, system = self._get_topic_and_system(line)
                if not system.isalpha():
                    system = int(system)
                    precisions, recalls, f1s = [], [], []
                    index += 2  # skip 'Fast score calc...'
                    while lines[index] != '...done':
                        precision, recall, f1 = self._get_f1(lines[index])
                        precisions.append(precision)
                        recalls.append(recall)
                        f1s.append(f1)
                        index += 1

                    metrics_dicts[topic][system]['BEwTE'] = {
                        'precision': sum(precisions) / len(precisions),
                        'recall': sum(recalls) / len(recalls),
                        'f1': sum(f1s) / len(f1s)
                    }
            index += 1

        metrics_lists = []
        for i in range(len(metrics_dicts)):
            metrics_list = []
            for j in range(len(metrics_dicts[i])):
                metrics_list.append(metrics_dicts[i][j])
            metrics_lists.append(metrics_list)
        return metrics_lists

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        with TemporaryDirectory() as temp_dir:
            self._save_summaries(temp_dir, summaries_list, references_list)

            self._run_step1(temp_dir)
            self._run_step2(temp_dir)
            self._run_step3(temp_dir)
            stdout = self._run_step4(temp_dir)

            # There is a weird way to score a summary given multiple references
            # in the original code. They multiply the highest recall score by
            # (num_references - 1) and adds that to the second to last score and
            # divides by num_references.
            # (See https://github.com/igorbrigadir/ROUGE-BEwTE/blob/f69a85556c889b805c89c5c71d7b77a983e75a05/src/main/java/bewte/BEwT_E.java#L419)
            # I don't understand this because it depends on the order that the
            # summaries are processed. We instead compute the average over the references.
            metrics_lists = self._parse_stdout(stdout)
            return metrics_lists


class BEwTESetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('bewte')
        self.parser.set_defaults(subfunc=self.run)

    def _edit_pom(self, file_path: str) -> None:
        # We need to edit the pom.xml file to add options to run the main classes
        lines = open(file_path, 'r').read().splitlines()
        with open(file_path, 'w') as out:
            for line in lines[:80]:
                out.write(line + '\n')
            out.write('''
                <plugin>
                    <groupId>org.codehaus.mojo</groupId>
                    <artifactId>exec-maven-plugin</artifactId>
                    <version>1.6.0</version>
                    <executions>
                      <execution>
                        <id>RunPipe</id>
                        <configuration>
                          <mainClass>tratz.runpipe.util.RunPipe</mainClass>
                        </configuration>
                      </execution>
                      <execution>
                        <id>BEXpander</id>
                        <configuration>
                          <mainClass>bewte.BEXpander</mainClass>
                        </configuration>
                      </execution>
                      <execution>
                        <id>BEwT_E</id>
                        <configuration>
                          <mainClass>bewte.BEwT_E</mainClass>
                        </configuration>
                      </execution>
                    </executions>
                </plugin>
            ''')
            for line in lines[80:]:
                out.write(line + '\n')

    @overrides
    def run(self, args):
        assert command_exists('mvn'), 'BEwTE requires Maven to be installed'
        assert command_exists('git-lfs'), 'BEwTE requires git-lfs to be installed'

        commands = [
            f'mkdir -p {DATA_ROOT}/metrics',
            f'cd {DATA_ROOT}/metrics',
            f'git clone https://github.com/igorbrigadir/ROUGE-BEwTE'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()
        if process.returncode != 0:
            print('BEwT-E setup failure')
            return

        self._edit_pom(f'{DATA_ROOT}/metrics/ROUGE-BEwTE/pom.xml')

        commands = [
            f'cd {DATA_ROOT}/metrics/ROUGE-BEwTE',
            f'mvn package'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()
        if process.returncode == 0:
            print('BEwT-E setup success')
        else:
            print('BEwT-E setup failure')
