from .models import Person, AgencyEdge, Action, Phase, \
    Sector, Variable, MentalEdge, Category, \
    Power, PowerEdge
import networkx as nx


class Networks:
    def __init__(self, phase):

        self.phase = phase
        self.alter = nx.Graph()

        for e in EgoEdge.objects.filter(phase=phase):
            self.alter.add_edge(e.source, e.target,
                                distance=e.distance,
                                interaction=e.interaction)

    def update_alter_metrics(self):
        degrees = list(self.alter.degree())
        for node in degrees:
            node[0].degree = node[1]
            node[0].save()

    def update_action_metrics(self):
        for a in Action.objects.all():
            a.update_in_degree(self.phase)
            a.save()


class AgencyNetwork:
    def __init__(self, ego_ids, phase_id):
        phase = Phase.objects.get(pk=phase_id)
        g = nx.DiGraph()
        for ego_id in ego_ids:
            ego = Person.objects.get(id=ego_id)

            # create network from egos to alters
            for e in ego.ego_net.filter(phase=phase):
                if e.source.name.startswith('TL'):
                    g.add_node(e.source.id,
                               name=e.source.name,
                               shape="ellipse",
                               width=260,
                               height=260,
                               avatar=e.source.avatar_url(),
                               href='/alter/%s/' % e.source.id,
                               scolor=colors.sector_color(e.source))
                else:
                    g.add_node(e.source.id,
                               name=e.source.name,
                               shape="ellipse",
                               width=160,
                               height=100,
                               href='/alter/%s/' % e.source.id,
                               scolor=colors.sector_color(e.source))
                for action_e in ActionEdge.objects.filter(
                        alter=e.source).filter(phase=phase):
                    g.add_node(action_e.action.action,
                               name=action_e.action.action,
                               shape='rectangle',
                               width=160,
                               height=100,
                               href='/action/%s/' % action_e.action.id,
                               scolor=colors.practice_color(
                                   action_e.action))
                    g.add_edge(action_e.alter.id,
                               action_e.action.action)

                if e.target.name.startswith('TL0'):
                    g.add_node(e.target.id,
                               name=e.target.name,
                               shape="ellipse",
                               width=260,
                               height=260,
                               avatar=e.target.avatar_url(),
                               href='/alter/%s/' % e.target.id,
                               scolor=colors.sector_color(e.target))
                else:
                    g.add_node(e.target.id,
                               name=e.target.name,
                               shape="ellipse",
                               width=160,
                               height=100,
                               href='/alter/%s/' % e.target.id,
                               scolor=colors.sector_color(e.target))
                for action_e in ActionEdge.objects.filter(
                        alter=e.target).filter(phase=phase):
                    g.add_node(action_e.action.action,
                               name=action_e.action.action,
                               shape='rectangle',
                               width=160,
                               height=100,
                               href='/action/%s/' % action_e.action.id,
                               scolor=colors.practice_color(
                                   action_e.action))
                    g.add_edge(action_e.alter.id,
                               action_e.action.action)

                g.add_edge(e.source.id,
                           e.target.id,
                           distance=4 - e.distance,
                           polarity=e.polarity,
                           i_s=e.influence_source,
                           i_t=e.influence_target)

        self.g = g

    def get_json(self):
        net = {'nodes': [{'data': {'id': n,
                                   'href': self.g.node[n]['href'],
                                   'name': self.g.node[n]['name'],
                                   'shape': self.g.node[n]['shape'],
                                   'width': self.g.node[n]['width'],
                                   'height': self.g.node[n]['height'],
                                   'avatar': "%s"
                                   % self.g.node[n].get('avatar', '/media/'),
                                   'scolor': self.g.node[n]['scolor']}}
                         for n in self.g.nodes],
               'edges': [{'data':
                          {'source': e[0],
                           'target': e[1],
                           'source_label': self.g.get_edge_data(
                               *e).get('i_s', ''),
                           'target_label': self.g.get_edge_data(
                               *e).get('i_t', ''),
                           'distance': self.g.get_edge_data(
                               *e).get('distance', 0),
                           'polarity': "crimson"
                           if self.g.get_edge_data(*e).get('polarity', 0) == -1
                           else "cornflowerblue"
                           if self.g.get_edge_data(*e).get('polarity', 0) == 1
                           else "grey"}}
                         for e in self.g.edges]}
        return net


class MentalModel:
    def __init__(self, ego_ids, phase_id):
        phase = Phase.objects.get(pk=phase_id)
        g = nx.DiGraph()
        for ego_id in ego_ids:
            ego = Person.objects.get(id=ego_id)
            h = ego.mental_model(phase)

            g = nx.compose(g, h)

        for ego_id in ego_ids:
            ego = Person.objects.get(id=ego_id)
            h = ego.mental_model(phase)
            for n in h.nodes:
                if n in g.nodes:
                    if 'egos' in g.node[n]:
                        g.node[n]['egos'].append(ego)
                    else:
                        g.node[n]['egos'] = [ego, ]

        self.g = g

    def get_json(self):
        net = {'nodes': [{'data': {'id': n,
                                   'shape': self.g.node[n]['shape']}}
                         for n in self.g.nodes],
               'edges': [{'data': {'source': e[0],
                                   'target': e[1]}} for e in self.g.edges]}
        return net

    def get_compound_json(self):

        net = {
            'nodes': [
                {'data': {'id': n, 'name': n}}
                for n in self.g.nodes],
            'edges': [{'data': {'source': e[0],
                                'target': e[1]}} for e in self.g.edges]}

        i = 0
        for n in self.g.nodes:
            for ego in self.g.node[n]['egos']:
                net['nodes'].append({'data': {'id': ego.name + " " + str(i),
                                              'name': ego.name,
                                              'parent': n}})
                i += 1
        return net


class PowerNetwork:
    def __init__(self, ego_ids, phase_id):
        phase = Phase.objects.get(pk=phase_id)
        g = nx.Graph()
        for ego_id in ego_ids:
            ego = Person.objects.get(id=ego_id)
            h = ego.power_network(phase)
            g = nx.compose(g, h)

        self.g = g

    def get_json(self):
        net = {'nodes': [{'data': {'id': n,
                                   'shape': self.g.node[n]['shape'],
                                   'width': self.g.node[n]['width'],
                                   'height': self.g.node[n]['height'],
                                   'avatar': "%s"
                                   % self.g.node[n].get('avatar', '/media/')}}
                         for n in self.g.nodes],
               'edges': [{'data': {'source': e[0],
                                   'target': e[1]}} for e in self.g.edges]}
        return net
