from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from common.task import AsyncTask, PeriodicTask, ScheduledTask, Task, TaskFlag


class Request(BaseModel):
    command: str
    data: Union[Task, TaskFlag, Optional[TaskFlag],
                Tuple[TaskFlag, str]] = None

    def into_dict(self) -> Dict[str, Any]:
        """
        Convert request to dict.
        Reconstruct data to facilitate communication with 'rust'
        :return: Dict[str, Any]
        """
        data = self.model_dump()
        if data['data'] is None:
            return {"command": {"List": None}}
        if "task_type" not in data['data']:
            result = {"command": {}}
            result["command"][data["command"]] = data["data"]
            return result
        if isinstance(data["data"], dict):
            if "max_restart" in data["data"]["task_type"]:
                data["data"]["task_type"] = {
                    "Async": data["data"]["task_type"]}
            elif "interval" in data["data"]["task_type"]:
                data["data"]["task_type"] = {
                    "Periodic": data["data"]["task_type"]}
            elif "year" in data["data"]["task_type"]:
                data["data"]["task_type"] = {
                    "Scheduled": data["data"]["task_type"]}
            else:
                raise Exception("Unknown task type")
        result = {"command": {}}
        result["command"][data["command"]] = data["data"]
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Request":
        """
        Convert dict to request.
        Reconstruct data to facilitate communication with 'rust'
        :param data: Dict[str, Any]
        :return: Request
        """
        command = list(data["command"].keys())[0]
        data = data["command"][command]
        if command in ["Run", "Add", "Reload"]:
            if 'Async' in data["task_type"]:
                data["task_type"] = AsyncTask(
                    **data["task_type"]["Async"])
            elif 'Periodic' in data["task_type"]:
                data["task_type"] = PeriodicTask(
                    **data["task_type"]["Periodic"])
            elif 'Scheduled' in data["task_type"]:
                data["task_type"] = ScheduledTask(
                    **data["task_type"]["Scheduled"])
            else:
                raise Exception("Unknown task type")
            return cls(command=command, data=data)
        elif command in ["List"]:
            if data is None:
                return cls(command=command, data=None)
            else:
                return cls(command=command, data=TaskFlag(**data))
        else:
            return cls(command=command, data=TaskFlag(**data))


class Status(BaseModel):
    id: int
    group: Optional[str] = ""
    name: str
    command: str
    args: List[str]
    dir: Optional[str] = None
    env: Dict[str, str]
    stdin: Optional[bool] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    created_at: int
    task_type: Any
    pid: Optional[int] = None
    status: Optional[str] = None
    exit_code: Optional[int] = None


class Response(BaseModel):
    code: int
    msg: str
    data: Any

    def __init__(self, code: int, msg: str, data: Any = None) -> None:
        super().__init__(code=code, msg=msg, data=data)

    @classmethod
    def success(cls, data: Any = None) -> "Response":
        return cls(code=10000, msg="Success", data=data)

    @classmethod
    def wrong(cls, msg: str) -> "Response":
        return cls(code=40000, msg="Wrong", data=msg)

    @classmethod
    def failed(cls, msg: str) -> "Response":
        return cls(code=50000, msg="Failed", data=msg)

    def into_dict(self) -> Dict[str, Any]:
        """
        Convert response to dict.
        Reconstruct data to facilitate communication with 'rust' 
        :return: Dict[str, Any]
        """
        if isinstance(self.data, list):
            for item in self.data:
                if isinstance(item.task_type, AsyncTask):
                    item.task_type = {"Async": item.task_type}
                elif isinstance(item.task_type, PeriodicTask):
                    item.task_type = {"Periodic": item.task_type}
                elif isinstance(item.task_type, ScheduledTask):
                    item.task_type = {"Scheduled": item.task_type}
                else:
                    raise Exception("Unknown task type")
            self.data = {"Status": self.data}
        elif isinstance(self.data, str):
            self.data = {"String": self.data}
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Response":
        """
        Convert dict to response.
        Reconstruct data to facilitate communication with 'rust'
        :param data: Dict[str, Any]
        :return: Response
        """
        result = cls(**data)
        if isinstance(result.data, dict) and "Status" in result.data:
            for item in result.data["Status"]:
                if "Async" in item["task_type"]:
                    item["task_type"] = AsyncTask(
                        **item["task_type"]["Async"])
                elif "Periodic" in item["task_type"]:
                    item["task_type"] = PeriodicTask(
                        **item["task_type"]["Periodic"])
                elif "Scheduled" in item["task_type"]:
                    item["task_type"] = ScheduledTask(
                        **item["task_type"]["Scheduled"])
                else:
                    raise Exception("Unknown task type")
            result.data = [Status(**i) for i in result.data["Status"]]
        elif isinstance(result.data, dict) and "String" in result.data:
            result.data = result.data["String"]
        return result
