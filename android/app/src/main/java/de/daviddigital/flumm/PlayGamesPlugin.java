package de.daviddigital.flumm;

import android.content.Intent;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.android.gms.games.GamesSignInClient;
import com.google.android.gms.games.LeaderboardsClient;
import com.google.android.gms.games.PlayGames;
import com.google.android.gms.games.PlayGamesSdk;
import com.google.android.gms.games.leaderboard.Leaderboard;
import com.google.android.gms.games.leaderboard.LeaderboardVariant;
import com.google.android.gms.games.leaderboard.LeaderboardScore;
import com.google.android.gms.games.leaderboard.LeaderboardScoreBuffer;
import com.getcapacitor.JSArray;

/** Kleine eigene Brücke zu Google Play Spiele (PGS v2): Anmeldung und Bestenlisten. */
@CapacitorPlugin(name = "PlayGames")
public class PlayGamesPlugin extends Plugin {
    private boolean ready = false;

    @PluginMethod
    public void initialize(PluginCall call) {
        try {
            if (!ready) { PlayGamesSdk.initialize(getContext()); ready = true; }
            call.resolve();
        } catch (Exception e) { call.reject("init: " + e.getMessage()); }
    }

    @PluginMethod
    public void signIn(PluginCall call) {
        if (!ready) { call.reject("not initialized"); return; }
        boolean silent = call.getBoolean("silent", true);
        GamesSignInClient c = PlayGames.getGamesSignInClient(getActivity());
        (silent ? c.isAuthenticated() : c.signIn()).addOnCompleteListener(t -> {
            JSObject r = new JSObject();
            r.put("signedIn", t.isSuccessful() && t.getResult() != null && t.getResult().isAuthenticated());
            call.resolve(r);
        });
    }

    @PluginMethod
    public void submitScore(PluginCall call) {
        String id = call.getString("leaderboardId");
        Double score = call.getDouble("score");
        if (!ready || id == null || score == null) { call.reject("missing"); return; }
        String tag = call.getString("tag");
        if (tag != null && !tag.isEmpty()) PlayGames.getLeaderboardsClient(getActivity()).submitScore(id, score.longValue(), tag);
        else PlayGames.getLeaderboardsClient(getActivity()).submitScore(id, score.longValue());
        call.resolve();
    }

    @PluginMethod
    public void showLeaderboard(PluginCall call) {
        String id = call.getString("leaderboardId");
        if (!ready || id == null) { call.reject("missing"); return; }
        PlayGames.getLeaderboardsClient(getActivity()).getLeaderboardIntent(id)
            .addOnSuccessListener(this::open).addOnFailureListener(e -> call.reject(e.getMessage()))
            .addOnSuccessListener(i -> call.resolve());
    }

    @PluginMethod
    public void showAllLeaderboards(PluginCall call) {
        if (!ready) { call.reject("not initialized"); return; }
        PlayGames.getLeaderboardsClient(getActivity()).getAllLeaderboardsIntent()
            .addOnSuccessListener(this::open).addOnFailureListener(e -> call.reject(e.getMessage()))
            .addOnSuccessListener(i -> call.resolve());
    }

    /** Anzahl Spieler mit Ergebnis in einer Bestenliste (span: daily|weekly|all). */
    @PluginMethod
    public void getPlayerCount(PluginCall call) {
        String id = call.getString("leaderboardId");
        String span = call.getString("span", "daily");
        if (!ready || id == null) { call.reject("missing"); return; }
        final int ts = "weekly".equals(span) ? LeaderboardVariant.TIME_SPAN_WEEKLY : "all".equals(span) ? LeaderboardVariant.TIME_SPAN_ALL_TIME : LeaderboardVariant.TIME_SPAN_DAILY;
        PlayGames.getLeaderboardsClient(getActivity()).loadTopScores(id, ts, LeaderboardVariant.COLLECTION_PUBLIC, 1, true)
            .addOnSuccessListener(data -> {
                long n = -1;
                LeaderboardsClient.LeaderboardScores sc = data.get();
                if (sc != null) {
                    Leaderboard lb = sc.getLeaderboard();
                    if (lb != null) for (LeaderboardVariant v : lb.getVariants()) {
                        if (v.getTimeSpan() == ts && v.getCollection() == LeaderboardVariant.COLLECTION_PUBLIC) { n = numScores(v); }
                    }
                    sc.release();
                }
                JSObject r = new JSObject(); r.put("count", n); call.resolve(r);
            })
            .addOnFailureListener(e -> call.reject(e.getMessage()));
    }

    /** Top-Ergebnisse inkl. Score-Tag laden (für eigene Bestenlisten-Ansicht). */
    @PluginMethod
    public void loadTopScores(PluginCall call) {
        String id = call.getString("leaderboardId");
        String span = call.getString("span", "daily");
        int max = call.getInt("max", 25);
        boolean centered = call.getBoolean("centered", false);
        if (!ready || id == null) { call.reject("missing"); return; }
        final int ts = "weekly".equals(span) ? LeaderboardVariant.TIME_SPAN_WEEKLY : "all".equals(span) ? LeaderboardVariant.TIME_SPAN_ALL_TIME : LeaderboardVariant.TIME_SPAN_DAILY;
        LeaderboardsClient lc = PlayGames.getLeaderboardsClient(getActivity());
        (centered ? lc.loadPlayerCenteredScores(id, ts, LeaderboardVariant.COLLECTION_PUBLIC, max, true)
                  : lc.loadTopScores(id, ts, LeaderboardVariant.COLLECTION_PUBLIC, max, true))
            .addOnSuccessListener(data -> {
                JSArray arr = new JSArray();
                LeaderboardsClient.LeaderboardScores sc = data.get();
                if (sc != null) {
                    LeaderboardScoreBuffer buf = sc.getScores();
                    for (LeaderboardScore x : buf) {
                        JSObject o = new JSObject();
                        o.put("rank", x.getRank());
                        o.put("name", x.getScoreHolderDisplayName());
                        o.put("score", x.getRawScore());
                        o.put("tag", x.getScoreTag());
                        try { o.put("playerId", x.getScoreHolder() != null ? x.getScoreHolder().getPlayerId() : ""); } catch (Exception ignored) {}
                        arr.put(o);
                    }
                    buf.release();
                    sc.release();
                }
                JSObject r = new JSObject(); r.put("scores", arr); call.resolve(r);
            })
            .addOnFailureListener(e -> call.reject(e.getMessage()));
    }

    @PluginMethod
    public void getPlayerId(PluginCall call) {
        if (!ready) { call.reject("not initialized"); return; }
        PlayGames.getPlayersClient(getActivity()).getCurrentPlayer()
            .addOnSuccessListener(pl -> { JSObject r = new JSObject(); r.put("playerId", pl.getPlayerId()); r.put("name", pl.getDisplayName()); call.resolve(r); })
            .addOnFailureListener(e -> call.reject(e.getMessage()));
    }

    private static long numScores(LeaderboardVariant v) {
        for (String m : new String[] {"getNumScores", "getNumRawScores"}) {
            try { Object r = v.getClass().getMethod(m).invoke(v); if (r instanceof Number) return ((Number) r).longValue(); } catch (Exception ignored) {}
        }
        return -1;
    }

    private void open(Intent i) { getActivity().startActivityForResult(i, 9004); }
}
