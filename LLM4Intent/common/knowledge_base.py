import networkx as nx
from LLM4Intent.common.utils import get_logger
from LLM4Intent.tools.jsonrpc import get_address_type_from_jsonrpc


# Transaction Graph Retrieval Generation
class MemoryGraph:
    def __init__(self):
        self.log = get_logger("MemoryGraph")
        self.g = nx.MultiDiGraph()

    def get_coverage(self):

        coverage = {
            "EOA": 0,
            "Transaction": 0,
            "Contract": 0,
        }

        for n, attrs in self.g.nodes:
            if attrs["type"] == "EOA":
                coverage["EOA"] += 1
            elif attrs["type"] == "Contract":
                coverage["Contract"] += 1

        for u, v, k, attrs in self.g.edges(keys=True, data=True):
            if attrs["type"] == "Transaction":
                coverage["Transaction"] += 1

    # describe the whole graph in a cypher script
    def get_encoding(self):
        cypher = ""
        for n, attrs in self.g.nodes(data=True):
            if attrs.get("type") == "EOA":
                attrs["type"] = "EOA"
            elif attrs.get("type") == "CA":
                attrs["type"] = "CA"
            else:
                self.log.warning(f"Unknown address type: {attrs.get("type")}")
                attrs["type"] = get_address_type_from_jsonrpc(n)

            cypher += "CREATE ({n}: {{{attrs}}}) \n".format(n=n, attrs=attrs)

        for u, v, k, attrs in self.g.edges(keys=True, data=True):
            print(attrs)
            cypher += "MERGE ({u})-[{k}:{kind} {{{attrs}}}]->({v})\n".format(
                u=u, v=v, k=k, kind=attrs["type"], attrs=attrs
            )

        return cypher

    # transaction is a dictionary from jsonrpc
    def add_transaction(self, transaction):
        transaction_attributes = dict(transaction.copy())
        transaction_attributes.pop("from")
        transaction_attributes.pop("to")
        transaction_attributes.pop("hash")

        transaction_attributes["type"] = "transaction"

        if not self.g.has_node(transaction["from"]):
            # determine the kind
            self.g.add_node(
                transaction["from"],
                kind=get_address_type_from_jsonrpc(transaction["from"]),
            )

        if not self.g.has_node(transaction["to"]):
            # determine the kind
            self.g.add_node(
                transaction["to"], kind=get_address_type_from_jsonrpc(transaction["to"])
            )

        self.g.add_edge(
            transaction["from"],
            transaction["to"],
            transaction["hash"],
            **transaction_attributes,
        )

    # transfer is a decoded transfer log from the transaction receipt
    def add_transfer(self, transfer):
        transfer_attributes = transfer.copy()
        transfer_attributes.pop("from")
        transfer_attributes.pop("to")
        transfer_attributes.pop("index")

        transfer_attributes["type"] = "transfer"

        if not self.g.has_node(transfer["from"]):
            # determine the kind
            self.g.add_node(
                transfer["from"], kind=get_address_type_from_jsonrpc(transfer["from"])
            )

        if not self.g.has_node(transfer["to"]):
            # determine the kind
            self.g.add_node(
                transfer["to"], kind=get_address_type_from_jsonrpc(transfer["to"])
            )

        self.g.add_edge(
            transfer["from"],
            transfer["to"],
            transfer["hash"] + "." + transfer["index"],
            **transfer_attributes,
        )

    # set additional attributes to the transaction
    def enrich_edge(self, u, v, k, key, value):
        self.g.edges[u, v, k][key] = value

    # set additional attributes to the address
    def enrich_node(self, address, key, value):
        self.g.nodes[address][key] = value
