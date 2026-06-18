"""적재된 금융 용어(Term)로 AI 4지선다 퀴즈(Quiz)를 사전 배치 생성한다.

사용 예:
	python manage.py generate_quizzes --limit 5
	python manage.py generate_quizzes --skip-existing
"""

import random

from django.core.management.base import BaseCommand

from tutors.models import Term, Quiz
from tutors.quiz_generator import generate_quiz_for_term


def build_question(term_name):
	"""용어명으로 퀴즈 질문 문구를 만든다(중복 판별 기준도 이 문구를 사용)."""
	return f"다음 용어의 뜻으로 옳은 것은? — {term_name}"


class Command(BaseCommand):
	help = '적재된 금융 용어로 AI 4지선다 퀴즈를 생성하여 Quiz 테이블에 저장합니다.'

	def add_arguments(self, parser):
		parser.add_argument('--limit', type=int, default=None, help='생성할 퀴즈 최대 개수')
		parser.add_argument(
			'--skip-existing',
			action='store_true',
			help='이미 퀴즈가 만들어진 용어는 건너뜁니다.',
		)

	def handle(self, *args, **options):
		limit = options['limit']
		skip_existing = options['skip_existing']

		terms = Term.objects.all().order_by('id')
		existing_questions = set(Quiz.objects.values_list('question', flat=True))

		created = 0
		for term in terms:
			if limit is not None and created >= limit:
				break

			question = build_question(term.term_name)
			if skip_existing and question in existing_questions:
				continue

			try:
				item = generate_quiz_for_term(term.term_name, term.explanation)
			except Exception as exc:
				self.stdout.write(self.style.WARNING(f"[건너뜀] '{term.term_name}' 생성 실패: {exc}"))
				continue

			# 모델이 오답을 3개보다 많거나 적게 줄 수 있으므로 정확히 3개로 맞춘다.
			distractors = [d for d in item.distractors if d != item.correct_choice][:3]
			if len(distractors) < 3:
				self.stdout.write(self.style.WARNING(f"[건너뜀] '{term.term_name}' 오답 부족({len(distractors)}개)"))
				continue

			options_list = [item.correct_choice] + distractors
			random.shuffle(options_list)

			Quiz.objects.create(
				question=question,
				options=options_list,
				answer=item.correct_choice,
				explanation=term.explanation,
			)
			existing_questions.add(question)
			created += 1
			self.stdout.write(f"  생성: {term.term_name}")

		self.stdout.write(self.style.SUCCESS(f"{created}개의 퀴즈가 생성되었습니다."))
