setTimeout(function() {
    function getCurrentTime() {
        return new Date().toLocaleString();
    }

    function inspectObject(obj) {
        var result = {};
        var fields = obj.class.getDeclaredFields();
        fields.forEach(function(field) {
            field.setAccessible(true);
            try {
                var value = field.get(obj);
                if (value === null) {
                    result[field.getName()] = "null";
                } else if (typeof value === 'number' || typeof value === 'string') {
                    result[field.getName()] = value;
                } else {
                    result[field.getName()] = value.toString();
                }
            } catch (e) {
                result[field.getName()] = e.toString();
            }
        });
        return result;
    }

    // Java.perform(function () {
    //     var b = Java.use('tv.b');
    //     b.e.implementation = function (string_arg) {
    //         console.log(`[${getCurrentTime()}] b.e called with:`, string_arg);
    //         var rev = this.e(string_arg);
    //         console.log(`[${getCurrentTime()}] Return value of b.e:`, rev)
    //         console.log(`[${getCurrentTime()}]`, this.f74344a)
    //         return rev
    //     };
    // });
    // Java.perform(function () {
    //     var a = Java.use('tv.a');
    //     a.e.implementation = function (string_arg) {
    //         // Print the time in every console.log
    //         var rev = this.e(string_arg);
    //         console.log(`[${getCurrentTime()}] Return value of a.e:`, rev)
    //         console.log(`[${getCurrentTime()}]`, this.f74344a)
    //         return rev
    //     };
    // });
    
    // public final T c(@NonNull Map<String, String> map) {
    //     try {
    //         return b(map);
    //     } catch (Exception unused) {
    //         return this.f71825a;
    //     }
    // }
    // Java.perform(function () {
    //     var m30a = Java.use('m30.a');
    //     m30a.c.implementation = function (map) {
    //         console.log(`[${getCurrentTime()}] m30.a.c called with:`, JSON.stringify(inspectObject(map)));
    //         var rev = this.c(map);
    //         console.log(`[${getCurrentTime()}] Return value of m30.a.c:`, JSON.stringify(inspectObject(rev)))
    //         console.log(`[${getCurrentTime()}]`, this.f71825a)
    //         return rev
    //     };
    // });

    /*
    package com.moovit.app.subscription;

    public class a0{
        // compiled from: MoovitSubscriptionsManager
        public static class d {
            public static int a(@NonNull Context context, @NonNull List<PurchaseDetails> list, @NonNull List<k> list2) {
                    if (((Boolean) x30.b.a(context, qv.a.f73530a)).booleanValue() || !list2.isEmpty()) {
                        return 3;
                    }
                    if (!list.isEmpty()) {
                        return 2;
                    }
                    return 1;
                }

            public d(@NonNull Context context, @NonNull List<PurchaseDetails> list, @NonNull List<k> my_subscriptionsList) {
                this.f65295a = a(context, list, my_subscriptionsList);
                this.purchaseDetailsList = Collections.unmodifiableList(list);
                this.my_subsctiptionsList = Collections.unmodifiableList(my_subscriptionsList);
            }
    */
    Java.perform(function () {
        var a0 = Java.use('com.moovit.app.subscription.a0$d');
        a0.$init.implementation = function (context, list1, list2) {
            console.log(`[${getCurrentTime()}] a0.d called with:`, JSON.stringify(inspectObject(context)), JSON.stringify(inspectObject(list1)), JSON.stringify(inspectObject(list2)));
            var rev = this.d(context, list1, list2);
            console.log(`[${getCurrentTime()}] Return value of a0.d:`, rev)
            console.log(`[${getCurrentTime()}]`, this.f65295a);
            return rev;
        };
    });

    /*
    package n30;
    public abstract class h<T> extends a.b<T> {
        public final T b(@NonNull Map<String, String> map) throws Exception {
            String str = map.get(this.f72322b);
            if (str != null) {
                return d(str);
            }
            throw new IllegalStateException("Missing configuration key: " + this.f72322b);
        }
    */
    // Java.perform(function () {
    //     var h = Java.use('n30.h');
    //     h.b.implementation = function (map) {
    //         console.log(`[${getCurrentTime()}] n30.h.b called with:`, map, JSON.stringify(inspectObject(map)));
    //         console.log(`[${getCurrentTime()}] this.f72322b:`, this.f72322b);
    //         var rev = this.b(map);
    //         console.log(`[${getCurrentTime()}] Return value of n30.h.b:`, rev)
    //         return rev;
    //     };
    // });

    /*
    package com.moovit.app.subscription.premium.packages;
    public enum SubscriptionPackageState {
        INACTIVE((String) null),
        OFFER("package_state_offer"),
        PENDING_ACTIVATION("package_state_pending_activation"),
        ACTIVE("package_state_active");
    */
   // Change all enums to ACTIVE
    Java.perform(function () {
        var SubscriptionPackageStateEnum = Java.use('com.moovit.app.subscription.premium.packages.SubscriptionPackageState');
        SubscriptionPackageStateEnum.INACTIVE.value = SubscriptionPackageStateEnum.ACTIVE.value;
        SubscriptionPackageStateEnum.OFFER.value = SubscriptionPackageStateEnum.ACTIVE.value;
        SubscriptionPackageStateEnum.PENDING_ACTIVATION.value = SubscriptionPackageStateEnum.ACTIVE.value;
    });

    /*
    package xz;
    public final class b {
        public static final SubscriptionPackage b(SubscriptionPackageType subscriptionPackageType, MoovitApplication<?, ?, ?> moovitApplication) {
            switch (a.my_all_subscription_types[subscriptionPackageType.ordinal()]) {
    */
//    Java.perform(function () {
//         var b = Java.use('xz.b');
//         b.b.implementation = function (subscriptionPackageType, moovitApplication) {
//             console.log(`[${getCurrentTime()}] xz.b.b called with:`, subscriptionPackageType, moovitApplication);
//             console.log(`[${getCurrentTime()}] a`, this.a);
//             console.log(`[${getCurrentTime()}] a.my_all_subscription_types: `, this.a.my_all_subscription_types);
//             var rev = this.b(subscriptionPackageType, moovitApplication);
//             console.log(`[${getCurrentTime()}] Return value of xz.b.b:`, rev)
//             return rev;
//         };
//     });

    /*
    package xz;
    class a {
        public final List<SubscriptionPackage> d() {
        return this.f75413c;
    }
    */
    // Java.perform(function () {
    //     var a = Java.use('xz.a');
    //     a.d.implementation = function () {
    //         console.log(`[${getCurrentTime()}] xz.a.d called`);
    //         console.log(`[${getCurrentTime()}] f75413c:`, this.f75413c);
    //         console.log(`[${getCurrentTime()}] f75412b:`, this.f75412b);
    //         var rev = this.d();
    //         console.log(`[${getCurrentTime()}] Return value of xz.a.d:`, rev)

    //         return rev;
    //     };
    // });

    // Java.perform(function () {
    //     var sp = Java.use("android.app.SharedPreferencesImpl$EditorImpl");
    //     sp.putString.implementation = function (key, value) {
    //         console.log(`putString("${key}", "${value}")`);

    //         let outer = this.this$0.value; // SharedPreferencesImpl 
    //         console.log("pref file: " + outer.mFile.value);

    //         return this.putString(key, value);
    //     }

    //     sp.putBoolean.implementation = function (key, value) {
    //         console.log(`putBoolean("${key}", ${value})`);

    //         let outer = this.this$0.value; // SharedPreferencesImpl 
    //         console.log("pref file: " + outer.mFile.value);
            
    //         this.putBoolean("is_subscribed", true);
    //         return this.putBoolean(key, value);
    //     }
    
    //     // Add similar hooks for other put methods (putInt, putFloat, etc.)
    // });

    // Log if the functions below are called:
    // package com.moovit.app.subscription;
    /* compiled from: SubscriptionManager.kt */
    // public final class g0 {
    // public final SharedPreferences e() {
    //     SharedPreferences sharedPreferences = this.f65310a.getSharedPreferences("subscriptions_manager", 0);
    //     Intrinsics.checkNotNullExpressionValue(sharedPreferences, "getSharedPreferences(...)");
    //     return sharedPreferences;
    // }
    // public final boolean g() {
    //     return j.n().l("is_subscribed");
    // }
    // public final boolean h() {
    //     Object a5 = b.a(this.f65310a, qv.a.f73530a);
    //     Intrinsics.checkNotNullExpressionValue(a5, "get(...)");
    //     if (((Boolean) a5).booleanValue()) {
    //         return true;
    //     }
    //     return !f().isEmpty();
    // }
    // public final Set<String> f() {
    //     Set<String> a5 = this.f65311b.a(my_getSharedPrefrences());
    //     Intrinsics.checkNotNullExpressionValue(a5, "get(...)");
    //     return a5;
    // }

    Java.perform(function () {
        var g0 = Java.use('com.moovit.app.subscription.g0');
        g0.e.implementation = function () {
            // console.log(`[${getCurrentTime()}] com.moovit.app.subscription.g0.e called`);
            var rev = this.e();
            // console.log(`[${getCurrentTime()}] Return value of com.moovit.app.subscription.g0.e:`, rev)
            // console.log(`[${getCurrentTime()}] Return value of com.moovit.app.subscription.g0.e:`, JSON.stringify(inspectObject(rev)))
            return rev;
        };
        g0.g.implementation = function () {
            // console.log(`[${getCurrentTime()}] com.moovit.app.subscription.g0.g called`);
            var rev = this.g();
            // console.log(`[${getCurrentTime()}] Return value of com.moovit.app.subscription.g0.g:`, rev)
            return rev;
        };
        g0.h.implementation = function () {
            // console.log(`[${getCurrentTime()}] com.moovit.app.subscription.g0.h called`);
            var rev = this.h();
            // console.log(`[${getCurrentTime()}] Return value of com.moovit.app.subscription.g0.h:`, rev)
            return rev;
        };
        g0.f.implementation = function () {
            // console.log(`[${getCurrentTime()}] com.moovit.app.subscription.g0.f called`);
            var rev = this.f();
            // console.log(`[${getCurrentTime()}] Return value of com.moovit.app.subscription.g0.f:`, rev)
            // console.log(`[${getCurrentTime()}] Return value of com.moovit.app.subscription.g0.f:`, JSON.stringify(inspectObject(rev)))
            return rev;
        };
    });

    // Log if the functions below are called:
    // package com.moovit.app.subscription;
    // public class a0 {
    // public static class d {
    //     public static int a(@NonNull Context context, @NonNull List<PurchaseDetails> list, @NonNull List<k> list2) {
    //         // TODO: AYOOOO Hook on this with frida please to see what happens and whether it's called
    //         if (((Boolean) x30.b.a(context, qv.a.f73530a)).booleanValue() || !list2.isEmpty()) {
    //             return 3;
    //         }
    //         if (!list.isEmpty()) {
    //             return 2;
    //         }
    //         return 1;
    //     }
    Java.perform(function () {
        var MoovitSubscriptionsManager = Java.use('com.moovit.app.subscription.a0$d');
        MoovitSubscriptionsManager.a.implementation = function (context, list1, list2) {
            console.log(`[${getCurrentTime()}] com.moovit.app.subscription.a0$d.a called with:`, JSON.stringify(inspectObject(context)), JSON.stringify(inspectObject(list1)), JSON.stringify(inspectObject(list2)));
            var rev = this.a(context, list1, list2);
            console.log(`[${getCurrentTime()}] Return value of com.moovit.app.subscription.a0$d.a:`, rev)
            return rev;
        };
    });

    // Log if the functions below are called:
    // package com.moovit.app.subscription;
    // public final class g0 {
    // public static final class a extends t0<g0, Context> {
    // public static /* synthetic */ Intent i(a aVar, Context context, String str, SubscriptionPackageType subscriptionPackageType, String str2, boolean z5, int i2, Object obj) {
    // Java.perform(function () {
    //     var MoovitSubscriptionsManager = Java.use('com.moovit.app.subscription.g0$a');
    //     MoovitSubscriptionsManager.i.implementation = function (avar, context, str, subscriptionPackageType, str2, z5, i2, ob) {
    //         console.log(`[${getCurrentTime()}] com.moovit.app.subscription.g0$a.i called with:`, JSON.stringify(inspectObject(context)), "|", str, "|", subscriptionPackageType, "|", str2, "|", z5, "|", i2, "|", ob);
    //         var rev = MoovitSubscriptionsManager.i(avar, context, str, subscriptionPackageType, str2, z5, i2, ob);
    //         console.log(`[${getCurrentTime()}] Return value of com.moovit.app.subscription.g0$a.i:`, JSON.stringify(inspectObject(rev)))
    //         return null;
    //     };
    // });

    // package com.moovit.app.ads;
    // public class MoovitBannerAdView {
    // public MoovitBannerAdView(@NonNull Context context, AttributeSet attributeSet, int i2) {
    //     return;
    // }
    Java.perform(function () {
        var MoovitBannerAdView = Java.use('com.moovit.app.ads.MoovitBannerAdView');
        MoovitBannerAdView.$init.overload('android.content.Context', 'android.util.AttributeSet', 'int').implementation = function (context, attributeSet, i2) {
            // console.log(`[${getCurrentTime()}] com.moovit.app.ads.MoovitBannerAdView.$init called with:`, JSON.stringify(inspectObject(context)), JSON.stringify(inspectObject(attributeSet)), i2);
            var rev = this.$init(context, attributeSet, i2);
            // this.R(); // my_removeAndHideAd()
            return rev;
        };
    });
    Java.perform(function () {
        var MoovitBannerAdView = Java.use('com.moovit.app.ads.MoovitBannerAdView');
        MoovitBannerAdView.T.implementation = function () {
            console.log(`[${getCurrentTime()}] com.moovit.app.ads.MoovitBannerAdView.T called`);
            // var rev = this.T();
            return;
        };
    });
    Java.perform(function () {
        var MoovitAdView = Java.use('com.moovit.app.ads.MoovitAdView');
        MoovitAdView.R.implementation = function () {
            console.log(`[${getCurrentTime()}] com.moovit.app.ads.MoovitAdView.R called`);
            // var rev = this.R();
            return;
        };
    });

    // NOT THE FULL SCREEN AD...
    // package com.moovit.ads;
    // public final class HtmlInterstitialAd extends InterstitialAd {
    // public HtmlInterstitialAd(@NotNull String str, @NotNull String str2, @NotNull InterstitialAdCreativeHtml interstitialAdCreativeHtml) {
    Java.perform(function () {
        var HtmlInterstitialAd = Java.use('com.moovit.ads.HtmlInterstitialAd');
        HtmlInterstitialAd.$init.overload('java.lang.String', 'java.lang.String', 'com.moovit.ads.interstitial.html.InterstitialAdCreativeHtml').implementation = function (str, str2, interstitialAdCreativeHtml) {
            console.log(`[${getCurrentTime()}] com.moovit.ads.HtmlInterstitialAd.$init called with:`, str, str2, JSON.stringify(inspectObject(interstitialAdCreativeHtml)));
            var rev = this.$init(str, str2, interstitialAdCreativeHtml);
            return rev;
        };
    });

    // NOT THE FULL SCREEN AD...
    // package com.moovit.ads;
    // public abstract class InterstitialAd extends Ad {
    // public InterstitialAd(String str, String str2) {
    Java.perform(function () {
        var InterstitialAd = Java.use('com.moovit.ads.InterstitialAd');
        InterstitialAd.$init.overload('java.lang.String', 'java.lang.String').implementation = function (str, str2) {
            console.log(`[${getCurrentTime()}] com.moovit.ads.InterstitialAd.$init called with:`, str, str2);
            var rev = this.$init(str, str2);
            return rev;
        };
    });

    // NOT THE FULL SCREEN AD... DOESNT GET CALLED because facebook ads are not used?
    // package com.facebook.ads;
    // public class RewardedInterstitialAd implements FullScreenAd {
    //     public boolean show() {
    //         return this.mRewardedInterstitialAdApi.show();
    //     }
    Java.perform(function () {
        var RewardedInterstitialAd = Java.use('com.facebook.ads.RewardedInterstitialAd');
        RewardedInterstitialAd.show.overload().implementation = function () {
            console.log(`[${getCurrentTime()}] com.facebook.ads.RewardedInterstitialAd.show called`);
            var rev = this.show();
            return rev;
        };
        var InterstitialAd = Java.use('com.facebook.ads.InterstitialAd');
        InterstitialAd.show.overload().implementation = function () {
            console.log(`[${getCurrentTime()}] com.facebook.ads.InterstitialAd.show called`);
            var rev = this.show();
            return rev;
        };
        var RewardedVideoAd = Java.use('com.facebook.ads.RewardedVideoAd');
        RewardedVideoAd.show.overload().implementation = function () {
            console.log(`[${getCurrentTime()}] com.facebook.ads.RewardedVideoAd.show called`);
            var rev = this.show();
            return rev;
        };
    });

    // NOT THE FULL SCREEN AD... DOESNT GET CALLED because facebook ads are not used?
    // package k9;
    // public class b implements p, InterstitialAdExtendedListener {
    //     public b(r rVar, e<p, q> eVar, d dVar) {
    Java.perform(function () {
        var b = Java.use('k9.b');
        b.$init.overload('mc.r', 'mc.e', 'j9.d').implementation = function (r, e, d) {
            console.log(`[${getCurrentTime()}] k9.b.$init called with:`, JSON.stringify(inspectObject(r)), JSON.stringify(inspectObject(e)), JSON.stringify(inspectObject(d)));
            var rev = this.$init(r, e, d);
            return rev;
        };
    });

    // FOUND the AdsManager!!! 🥳🥳🥳
    // package lu;
    // public class k0 {
        // public boolean U() {
        //     return j.n().l("is_ads_free_version");
        // }
    Java.perform(function () {
        var k0 = Java.use('lu.k0');
        k0.U.implementation = function () {
            // console.log(`[${getCurrentTime()}] lu.k0.U called`);
            var rev = this.U();
            console.log(`[${getCurrentTime()}] lu.k0.U return value:`, rev, "... returning true");
            return rev;
        };
        // public final String z(@NonNull MoovitComponentActivity moovitComponentActivity, @NonNull AdSource adSource, @NonNull String str) {
        k0.z.implementation = function (moovitComponentActivity, adSource, str) {
            console.log(`[${getCurrentTime()}] lu.k0.z called with:`, JSON.stringify(inspectObject(moovitComponentActivity)), "|", JSON.stringify(inspectObject(adSource)), "|", str);
            var rev = this.z(moovitComponentActivity, adSource, str);
            console.log(`[${getCurrentTime()}] lu.k0.z return value:`, rev);
            return rev;
        }
        // public void K0(@NonNull MoovitComponentActivity moovitComponentActivity, @NonNull AdSource adSource) {
        k0.K0.implementation = function (moovitComponentActivity, adSource) {
            console.log(`[${getCurrentTime()}] lu.k0.K0 called with:`, JSON.stringify(inspectObject(moovitComponentActivity)), "|", JSON.stringify(inspectObject(adSource)));
            var rev = this.K0(moovitComponentActivity, adSource);
            console.log(`[${getCurrentTime()}] lu.k0.K0 return value:`, rev);
            return;
        }
    });
}, 0);
