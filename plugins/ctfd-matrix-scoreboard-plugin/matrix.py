from flask import render_template
from CTFd import utils, scoreboard, challenges

from CTFd.models import db, Teams, Solves, Awards, Challenges
from sqlalchemy.sql import or_

ROOT = '/plugins/ctfd-matrix-scoreboard-plugin/'

def load(app):

    def get_standings():
        standings = scoreboard.get_standings()
        # TODO faster lookup here
        jstandings = []
        for team in standings:
            teamid = team[0]
            solves = db.session.query(Solves.chalid.label('chalid')).filter(Solves.teamid==teamid)
            freeze = utils.get_config('freeze')
            if freeze:
                freeze = utils.unix_time_to_utc(freeze)
                if teamid != session.get('id'):
                    solves = solves.filter(Solves.date < freeze)
            solves = solves.all()
            jsolves = []
            for solve in solves:
                jsolves.append(solve.chalid)


            jstandings.append({'teamid':team.teamid, 'score':team.score, 'name':team.name,'solves':jsolves})
        db.session.close()
        return jstandings
    def get_challenges():
        if not utils.is_admin():
            if not utils.ctftime():
                if utils.view_after_ctf():
                    pass
                else:
                    return []
        if utils.user_can_view_challenges() and (utils.ctf_started() or utils.is_admin()):
            chals = db.session.query(
                    Challenges.id,
                    Challenges.name,
                    Challenges.category
                ).filter(or_(Challenges.hidden != True, Challenges.hidden == None)).all()
            jchals = []
            for x in chals:
                jchals.append({
                    'id':x.id,
                    'name':x.name,
                    'category':x.category
                })
        return jchals



    def scoreboard_view():
        if utils.get_config('view_scoreboard_if_authed') and not utils.authed():
            return redirect(url_for('auth.login', next=request.path))
        if utils.hide_scores():
            return render_template('scoreboard-matrix.html', errors=['Scores are currently hidden'])
        standings = get_standings()
        return render_template('scoreboard-matrix.html', teams=standings,
            score_frozen=utils.is_scoreboard_frozen(), challenges=get_challenges())


    app.view_functions['scoreboard.scoreboard_view']  = scoreboard_view

