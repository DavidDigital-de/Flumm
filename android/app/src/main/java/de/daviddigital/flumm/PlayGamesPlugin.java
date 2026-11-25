package de.daviddigital.flumm;

import android.content.Intent;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.android.gms.games.GamesSignInClient;
import com.google.android.gms.games.PlayGames;
import com.google.android.gms.games.PlayGamesSdk;
import com.google.android.gms.games.leaderboard.Leaderboard;
import com.google.android.gms.games.leaderboard.LeaderboardVariant;

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
        PlayGames.getLeaderboardsClient(getActivity()).submitScore(id, score.longValue());
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
        PlayGames.getLeaderboardsClient(getActivity()).loadLeaderboardMetadata(id, true)
            .addOnSuccessListener(data -> {
                long n = -1;
                Leaderboard lb = data.get();
                if (lb != null) {
                    for (LeaderboardVariant v : lb.getVariants()) {
                        if (v.getTimeSpan() == ts && v.getCollection() == LeaderboardVariant.COLLECTION_PUBLIC) { n = v.getNumRawScores(); }
                    }
                }
                JSObject r = new JSObject(); r.put("count", n); call.resolve(r);
            })
            .addOnFailureListener(e -> call.reject(e.getMessage()));
    }

    private void open(Intent i) { getActivity().startActivityForResult(i, 9004); }
}
