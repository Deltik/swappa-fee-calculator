import argparse


class Constants:
    """Class to hold constants related to the fee calculations."""

    BUYER_FEE_RATE = 0.03
    SELLER_FEE_RATE = 0.03
    PAYPAL_FEE_RATE = 0.0349
    PAYPAL_FIXED_FEE = 0.49
    BOOST_FEE = 5.0


class FeeDeductions:
    """Class to handle fee deductions and calculations."""

    def __init__(
            self,
            ask_price: float,
            shipping_cost: float = 0.0,
            sales_tax: float = 0.0,
            featured: bool = False,
    ):
        self.ask_price = ask_price
        self.shipping_cost = shipping_cost
        self.sales_tax = sales_tax
        self.featured = featured

        # Calculations
        self.listing_price = self.ask_price * (1 + Constants.BUYER_FEE_RATE)
        self.buyer_paid = self.listing_price + (self.listing_price * (sales_tax / 100))
        self.buyer_fee = self.listing_price - self.ask_price
        self.seller_fee = self.ask_price * Constants.SELLER_FEE_RATE
        self.paypal_fee = (
                                  self.listing_price + (self.listing_price * (sales_tax / 100))
                          ) * Constants.PAYPAL_FEE_RATE + Constants.PAYPAL_FIXED_FEE

    def after_paypal(self) -> float:
        return self.ask_price - self.seller_fee - self.paypal_fee

    def after_shipping(self) -> float:
        return self.after_paypal() - self.shipping_cost

    def final_revenue(self) -> float:
        if self.featured:
            return self.after_shipping() - Constants.BOOST_FEE
        return self.after_shipping()


def formatted_output(fee_obj: FeeDeductions) -> str:
    """Formats the fee breakdown into a string for display."""
    lines = [
        (f"Buyer pays:", f"${fee_obj.buyer_paid:.2f}"),
        (
            f"Listing price:",
            f"${fee_obj.listing_price:.2f} (-${fee_obj.listing_price * (fee_obj.sales_tax / 100):.2f} sales tax @ {fee_obj.sales_tax:.2f}%)",
        ),
        (
            f"Ask price:",
            f"${fee_obj.ask_price:.2f} (-${fee_obj.buyer_fee:.2f} buyer fee @ {Constants.BUYER_FEE_RATE * 100:.2f}%)",
        ),
        (
            f"Swappa payout:",
            f"${fee_obj.ask_price - fee_obj.seller_fee:.2f} (-${fee_obj.seller_fee:.2f} seller fee @ {Constants.SELLER_FEE_RATE * 100:.2f}%)",
        ),
        (
            f"After PayPal:",
            f"${fee_obj.after_paypal():.2f} (-${fee_obj.paypal_fee:.2f} PayPal fee @ {Constants.PAYPAL_FEE_RATE * 100:.2f}% + ${Constants.PAYPAL_FIXED_FEE:.2f})",
        ),
    ]

    # Optional lines based on input data
    if fee_obj.shipping_cost:
        lines.append(
            (
                f"After shipping:",
                f"${fee_obj.after_shipping():.2f} (-${fee_obj.shipping_cost:.2f} shipping)",
            )
        )

    if fee_obj.featured:
        lines.append(
            (
                f"Final revenue:",
                f"${fee_obj.final_revenue():.2f} (-${Constants.BOOST_FEE:.2f} boost fee)",
            )
        )
    else:
        lines.append((f"Final revenue:", f"${fee_obj.final_revenue():.2f}"))

    # Format the lines for aligned output
    max_len = max(len(line[0]) for line in lines)
    return "\n".join(f"{line[0].ljust(max_len)} {line[1]}" for line in lines)


# Tests
def test_fee_calculator() -> None:
    test_cases = [
        {
            "input": {
                "ask_price": 868,
                "shipping_cost": 8.10,
                "sales_tax": 7.0,
                "featured": True,
            },
            "expected": """\
Buyer pays:     $956.62
Listing price:  $894.04 (-$62.58 sales tax @ 7.00%)
Ask price:      $868.00 (-$26.04 buyer fee @ 3.00%)
Swappa payout:  $841.96 (-$26.04 seller fee @ 3.00%)
After PayPal:   $808.08 (-$33.88 PayPal fee @ 3.49% + $0.49)
After shipping: $799.98 (-$8.10 shipping)
Final revenue:  $794.98 (-$5.00 boost fee)""",
        },
        {
            "input": {
                "ask_price": 200,
                "shipping_cost": 8.41,
                "sales_tax": 7.0,
                "featured": False,
            },
            "expected": """\
Buyer pays:     $220.42
Listing price:  $206.00 (-$14.42 sales tax @ 7.00%)
Ask price:      $200.00 (-$6.00 buyer fee @ 3.00%)
Swappa payout:  $194.00 (-$6.00 seller fee @ 3.00%)
After PayPal:   $185.82 (-$8.18 PayPal fee @ 3.49% + $0.49)
After shipping: $177.41 (-$8.41 shipping)
Final revenue:  $177.41""",
        },
        {
            "input": {
                "ask_price": 863,
                "shipping_cost": 8.55,
                "sales_tax": 0.0,
                "featured": False,
            },
            "expected": """\
Buyer pays:     $888.89
Listing price:  $888.89 (-$0.00 sales tax @ 0.00%)
Ask price:      $863.00 (-$25.89 buyer fee @ 3.00%)
Swappa payout:  $837.11 (-$25.89 seller fee @ 3.00%)
After PayPal:   $805.60 (-$31.51 PayPal fee @ 3.49% + $0.49)
After shipping: $797.05 (-$8.55 shipping)
Final revenue:  $797.05""",
        },
    ]

    for test in test_cases:
        fee_obj = FeeDeductions(**test["input"])
        result = formatted_output(fee_obj)
        assert (
                result == test["expected"]
        ), f"Expected:\n{test['expected']}\nGot:\n{result}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Swappa Fee Calculator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-a",
        "--ask",
        type=float,
        help="Ask price (whole number or with two decimal places)",
    )
    group.add_argument(
        "-l",
        "--listing",
        type=float,
        help="Listing price (real number with two decimal places)",
    )
    parser.add_argument(
        "-s", "--shipping", type=float, default=0.0, help="Shipping cost (optional)"
    )
    parser.add_argument(
        "-t",
        "--tax",
        type=float,
        default=0.0,
        help="Sales tax as a floating point percentage (optional)",
    )
    parser.add_argument(
        "-f",
        "--featured",
        action="store_true",
        help="Indicates whether the listing was featured (optional)",
    )
    args = parser.parse_args()

    # Calculate ask price if listing price is provided
    if args.listing:
        ask_price = round(args.listing / (1 + Constants.BUYER_FEE_RATE))
    else:
        ask_price = args.ask

    fee_obj = FeeDeductions(ask_price, args.shipping, args.tax, args.featured)
    print(formatted_output(fee_obj))


if __name__ == "__main__":
    test_fee_calculator()
    main()
