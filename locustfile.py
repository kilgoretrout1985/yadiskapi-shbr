from typing import Any, Dict, List

from locust import HttpUser, task

from tests import _give_2_folder_tree_import_batch


class YaDiskAPIUser(HttpUser):
    RUNS: int = 10

    def make_dataset(self):
        self.dataset: Dict[str, Any] = _give_2_folder_tree_import_batch(1000)
        self.dataset_ids: List[str] = [x['id'] for x in self.dataset['items']]
        self.dataset_dt: str = self.dataset['updateDate']

    @task
    def workflow(self):
        for _ in range(self.RUNS):
            self.make_dataset()

            # Минимальные требования:
            # импорт и удаление данных не превосходит 1000 элементов в 1 минуту
            self.post_imports()

            # RPS получения истории, недавних изменений и информации об элементе
            # суммарно не превосходит 100 запросов в секунду
            self.get_nodes_id()
            self.get_node_id_history()
            self.get_updates()

            # импорт и удаление данных не превосходит 1000 элементов в 1 минуту
            self.delete_delete_id()
        self.environment.runner.quit()  # иначе он будет крутиться бесконечно

    def post_imports(self):
        self.client.post("/imports", json=self.dataset, name="/imports")

    def get_nodes_id(self):
        for node_id in self.dataset_ids:
            self.client.get(f"/nodes/{node_id}", name="/nodes/id")

    def get_node_id_history(self):
        for node_id in self.dataset_ids:
            self.client.get(f"/node/{node_id}/history", name="/node/id/history")

    def get_updates(self):
        for i in range(1000):
            self.client.get(
                "/updates",
                params={"date": self.dataset_dt},
                name="/updates"
            )

    def delete_delete_id(self):
        # обходим с конца, чтобы сначала удалить все файлы и потом уже удалить
        # корневую папку, иначе первый запрос всё сотрет и потом будут 404
        for node_id in reversed(self.dataset_ids):
            self.client.delete(
                f"/delete/{node_id}",
                params={"date": self.dataset_dt},
                name="/delete/id"
            )
