import random
from typing import List

import textwrap
import helpers
import posprinter

routers, connections = helpers.load_from_file()

for router in routers:
    router_config: List[str] = router.generate_config()

    instructions = ("The world is in ashes, the internet is gone, and an evil power has taken over, enslaving humans "
                    "to act as routers in a shattered network. You are one of them, bound to guide packets using your "
                    "interfaces and routing table. Each decision determines the flow of what remains. Route swiftly, "
                    "route wisely. Resistance lives in the connections you maintain.")

    instruction_lines = textwrap.wrap(instructions, width=48)
    instruction_lines.insert(0, "-")
    instruction_lines.insert(0, "{PROTOCOL 666-" + str(random.randint(100,999)))
    instruction_lines.insert(0, "-")
    instruction_lines.append("")
    instruction_lines.extend(router_config)
    instruction_lines.append("-")

    [print(line) for line in instruction_lines]
    posprinter.print_pos(instruction_lines)
