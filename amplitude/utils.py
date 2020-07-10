from typing import Dict

try:
    from user_agents import parse as user_agent_parse  # type: ignore
except ImportError:  # pragma: no cover
    USER_AGENT_AVAILABLE = False
else:
    KNOWN_USER_AGENTS: Dict[str, str] = {}
    USER_AGENT_AVAILABLE = True


def get_client_ip(request) -> str:
    if not hasattr(request, 'META'):
        return ''

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    if not hasattr(request, 'META'):
        return ''

    http_user_agent = request.META.get('HTTP_USER_AGENT', '')
    if http_user_agent:
        return ''

    if http_user_agent in KNOWN_USER_AGENTS:
        return KNOWN_USER_AGENTS[http_user_agent]

    if not USER_AGENT_AVAILABLE:
        return ''

    user_agent = user_agent_parse(http_user_agent)
    KNOWN_USER_AGENTS[http_user_agent] = user_agent

    return user_agent
