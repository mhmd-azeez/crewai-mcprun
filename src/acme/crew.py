from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from acme.tools.servlet_tool import CryptoHashTool

crypto_hash_tool = CryptoHashTool(wasm_path="./crypto_hash.wasm")

@CrewBase
class Acme():
    """Acme crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def string_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['string_generator'],
            verbose=True
        )

    @agent 
    def hash_tester(self) -> Agent:
        return Agent(
            config=self.agents_config['hash_tester'],
            verbose=True,
            tools=[crypto_hash_tool]
        )

    @task
    def generate_strings(self) -> Task:
        return Task(
            config=self.tasks_config['generate_strings_task']
        )

    @task
    def hash_strings(self) -> Task:
        return Task(
            config=self.tasks_config['hash_strings_task'],
            output_file='hash_results.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Acme crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )