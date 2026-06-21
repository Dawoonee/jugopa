from django.db import migrations, models
from django.utils import timezone


def backfill_and_dedup(apps, schema_editor):
	"""기존 풀이 이력의 solved_date를 채우고, (user, solved_date) 중복은 가장 빠른 1건만 남긴다."""
	UserQuizHistory = apps.get_model('tutors', 'UserQuizHistory')

	# solved_at(datetime) → 로컬 날짜로 solved_date backfill
	for history in UserQuizHistory.objects.all().iterator():
		history.solved_date = timezone.localtime(history.solved_at).date()
		history.save(update_fields=['solved_date'])

	# (user, solved_date)별로 가장 먼저 푼 1건만 남기고 나머지 삭제
	seen = set()
	duplicate_ids = []
	for history in UserQuizHistory.objects.order_by('user_id', 'solved_date', 'solved_at').iterator():
		key = (history.user_id, history.solved_date)
		if key in seen:
			duplicate_ids.append(history.id)
		else:
			seen.add(key)
	if duplicate_ids:
		UserQuizHistory.objects.filter(id__in=duplicate_ids).delete()


def noop(apps, schema_editor):
	pass


class Migration(migrations.Migration):

	dependencies = [
		('tutors', '0001_initial'),
	]

	operations = [
		migrations.AddField(
			model_name='userquizhistory',
			name='user_choice',
			field=models.CharField(blank=True, default='', max_length=100, verbose_name='사용자 선택'),
		),
		migrations.AddField(
			model_name='userquizhistory',
			name='solved_date',
			field=models.DateField(null=True, verbose_name='풀이 일자'),
		),
		migrations.RunPython(backfill_and_dedup, noop),
		migrations.AlterField(
			model_name='userquizhistory',
			name='solved_date',
			field=models.DateField(verbose_name='풀이 일자'),
		),
		migrations.AlterUniqueTogether(
			name='userquizhistory',
			unique_together={('user', 'solved_date')},
		),
	]
