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

    Java.perform(function () {
        var sp = Java.use("android.app.SharedPreferencesImpl$EditorImpl");
        sp.putString.implementation = function (key, value) {
            console.log(`putString("${key}", "${value}")`);

            let outer = this.this$0.value; // SharedPreferencesImpl 
            console.log("pref file: " + outer.mFile.value);

            return this.putString(key, value);
        }

        sp.putBoolean.implementation = function (key, value) {
            console.log(`putBoolean("${key}", ${value})`);

            let outer = this.this$0.value; // SharedPreferencesImpl 
            console.log("pref file: " + outer.mFile.value);
            
            this.putBoolean("is_subscribed", true);
            return this.putBoolean(key, value);
        }
    
        // Add similar hooks for other put methods (putInt, putFloat, etc.)
    });
    
}, 0);
